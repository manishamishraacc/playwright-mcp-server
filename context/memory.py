import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import uuid

from schemas.mcp import Message, MessageRole, SessionInfo

logger = logging.getLogger(__name__)

class SessionManager:
    """In-memory session manager for storing conversation context"""
    
    def __init__(self, max_sessions: int = 100, session_ttl_hours: int = 24):
        self.sessions: Dict[str, Dict] = {}
        self.max_sessions = max_sessions
        self.session_ttl = timedelta(hours=session_ttl_hours)
        self._cleanup_task: Optional[asyncio.Task] = None
        
    async def initialize(self):
        """Initialize the session manager"""
        logger.info("Initializing session manager")
        # Start cleanup task
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        
    async def cleanup(self):
        """Cleanup resources"""
        logger.info("Cleaning up session manager")
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
                
    async def _cleanup_loop(self):
        """Background task to clean up expired sessions"""
        while True:
            try:
                await asyncio.sleep(3600)  # Run every hour
                await self._cleanup_expired_sessions()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
                
    async def _cleanup_expired_sessions(self):
        """Remove expired sessions"""
        now = datetime.utcnow()
        expired_sessions = []
        
        for session_id, session_data in self.sessions.items():
            last_activity = session_data.get('last_activity')
            if last_activity and (now - last_activity) > self.session_ttl:
                expired_sessions.append(session_id)
                
        for session_id in expired_sessions:
            await self.delete_session(session_id)
            logger.info(f"Cleaned up expired session: {session_id}")
            
    async def create_session(self, session_id: Optional[str] = None) -> str:
        """Create a new session"""
        if session_id is None:
            session_id = str(uuid.uuid4())
            
        if session_id in self.sessions:
            raise ValueError(f"Session {session_id} already exists")
            
        # Check if we need to remove old sessions
        if len(self.sessions) >= self.max_sessions:
            await self._remove_oldest_session()
            
        now = datetime.utcnow()
        self.sessions[session_id] = {
            'created_at': now,
            'last_activity': now,
            'messages': [],
            'metadata': {}
        }
        
        logger.info(f"Created new session: {session_id}")
        return session_id
        
    async def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session data"""
        session = self.sessions.get(session_id)
        if session:
            # Update last activity
            session['last_activity'] = datetime.utcnow()
        return session
        
    async def add_message(self, session_id: str, message: Message) -> bool:
        """Add a message to a session"""
        session = await self.get_session(session_id)
        if not session:
            return False
            
        session['messages'].append(message)
        session['last_activity'] = datetime.utcnow()
        
        # Keep only last 50 messages to prevent memory bloat
        if len(session['messages']) > 50:
            session['messages'] = session['messages'][-50:]
            
        logger.debug(f"Added message to session {session_id}")
        return True
        
    async def get_messages(self, session_id: str, limit: Optional[int] = None) -> List[Message]:
        """Get messages from a session"""
        session = await self.get_session(session_id)
        if not session:
            return []
            
        messages = session['messages']
        if limit:
            messages = messages[-limit:]
            
        return messages
        
    async def get_session_info(self, session_id: str) -> Optional[SessionInfo]:
        """Get session information"""
        session = await self.get_session(session_id)
        if not session:
            return None
            
        return SessionInfo(
            session_id=session_id,
            created_at=session['created_at'].isoformat(),
            message_count=len(session['messages']),
            last_activity=session['last_activity'].isoformat()
        )
        
    async def list_sessions(self) -> List[SessionInfo]:
        """List all active sessions"""
        sessions = []
        for session_id in self.sessions:
            session_info = await self.get_session_info(session_id)
            if session_info:
                sessions.append(session_info)
        return sessions
        
    async def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Deleted session: {session_id}")
            return True
        return False
        
    async def _remove_oldest_session(self):
        """Remove the oldest session when at capacity"""
        if not self.sessions:
            return
            
        oldest_session_id = min(
            self.sessions.keys(),
            key=lambda sid: self.sessions[sid]['last_activity']
        )
        await self.delete_session(oldest_session_id)
        
    async def update_metadata(self, session_id: str, key: str, value: any) -> bool:
        """Update session metadata"""
        session = await self.get_session(session_id)
        if not session:
            return False
            
        session['metadata'][key] = value
        session['last_activity'] = datetime.utcnow()
        return True
        
    async def get_metadata(self, session_id: str, key: str) -> Optional[any]:
        """Get session metadata"""
        session = await self.get_session(session_id)
        if not session:
            return None
        return session['metadata'].get(key) 