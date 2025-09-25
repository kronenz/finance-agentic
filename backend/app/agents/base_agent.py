# 기본 AI 에이전트 클래스
import asyncio
import uuid
import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime
import redis
import structlog

logger = structlog.get_logger()

class BaseAgent(ABC):
    """모든 AI 에이전트의 기본 클래스"""
    
    def __init__(self, agent_id: str, agent_name: str, redis_url: str = "redis://localhost:6379"):
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.redis_client = redis.from_url(redis_url)
        self.is_running = False
        self.message_handlers = {}
        self.correlation_id = None
        
        # 로깅 설정
        self.logger = structlog.get_logger(agent_name)
        
    async def start(self):
        """에이전트 시작"""
        self.is_running = True
        self.logger.info(f"Agent {self.agent_name} started", agent_id=self.agent_id)
        
        # 메시지 수신 루프 시작
        await self._message_loop()
        
    async def stop(self):
        """에이전트 중지"""
        self.is_running = False
        self.logger.info(f"Agent {self.agent_name} stopped", agent_id=self.agent_id)
        
    async def _message_loop(self):
        """메시지 수신 및 처리 루프"""
        while self.is_running:
            try:
                # Redis Streams에서 메시지 수신
                messages = self.redis_client.xread(
                    {f"agent:messages": "$"},
                    count=1,
                    block=1000  # 1초 대기
                )
                
                for stream, msgs in messages:
                    for msg_id, fields in msgs:
                        await self._process_message(msg_id, fields)
                        
            except Exception as e:
                self.logger.error(f"Error in message loop: {e}")
                await asyncio.sleep(1)
                
    async def _process_message(self, msg_id: str, fields: Dict[str, Any]):
        """메시지 처리"""
        try:
            # 메시지 파싱
            message = {
                "message_id": fields.get(b"message_id", b"").decode(),
                "correlation_id": fields.get(b"correlation_id", b"").decode(),
                "timestamp": fields.get(b"timestamp", b"").decode(),
                "sender_agent_id": fields.get(b"sender_agent_id", b"").decode(),
                "recipient_agent_id": fields.get(b"recipient_agent_id", b"").decode(),
                "task_name": fields.get(b"task_name", b"").decode(),
                "payload": json.loads(fields.get(b"payload", b"{}")),
                "status": fields.get(b"status", b"PENDING").decode(),
            }
            
            # 자신에게 온 메시지인지 확인
            if (message["recipient_agent_id"] == self.agent_id or 
                message["recipient_agent_id"] == "broadcast"):
                
                # 메시지 처리
                await self._handle_message(message)
                
                # ACK 전송
                self.redis_client.xack("agent:messages", "agent_group", msg_id)
                
        except Exception as e:
            self.logger.error(f"Error processing message: {e}")
            
    async def _handle_message(self, message: Dict[str, Any]):
        """메시지 핸들링 (하위 클래스에서 구현)"""
        task_name = message["task_name"]
        
        if task_name in self.message_handlers:
            try:
                await self.message_handlers[task_name](message)
            except Exception as e:
                self.logger.error(f"Error handling task {task_name}: {e}")
                await self._send_error_response(message, str(e))
        else:
            self.logger.warning(f"No handler for task: {task_name}")
            
    async def send_message(self, recipient: str, task_name: str, payload: Dict[str, Any], 
                          correlation_id: Optional[str] = None):
        """메시지 전송"""
        message = {
            "message_id": str(uuid.uuid4()),
            "correlation_id": correlation_id or str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "sender_agent_id": self.agent_id,
            "recipient_agent_id": recipient,
            "task_name": task_name,
            "payload": payload,
            "status": "PENDING"
        }
        
        # Redis Streams에 메시지 전송
        self.redis_client.xadd(
            "agent:messages",
            {
                "message_id": message["message_id"],
                "correlation_id": message["correlation_id"],
                "timestamp": message["timestamp"],
                "sender_agent_id": message["sender_agent_id"],
                "recipient_agent_id": message["recipient_agent_id"],
                "task_name": message["task_name"],
                "payload": json.dumps(message["payload"]),
                "status": message["status"]
            }
        )
        
        self.logger.info(f"Message sent", 
                        recipient=recipient, 
                        task_name=task_name,
                        message_id=message["message_id"])
        
    async def _send_error_response(self, original_message: Dict[str, Any], error: str):
        """에러 응답 전송"""
        await self.send_message(
            recipient=original_message["sender_agent_id"],
            task_name=f"{original_message['task_name']}_ERROR",
            payload={
                "error": error,
                "original_message_id": original_message["message_id"]
            },
            correlation_id=original_message["correlation_id"]
        )
        
    def register_handler(self, task_name: str, handler):
        """메시지 핸들러 등록"""
        self.message_handlers[task_name] = handler
        
    @abstractmethod
    async def initialize(self):
        """에이전트 초기화 (하위 클래스에서 구현)"""
        pass
        
    @abstractmethod
    async def cleanup(self):
        """에이전트 정리 (하위 클래스에서 구현)"""
        pass
