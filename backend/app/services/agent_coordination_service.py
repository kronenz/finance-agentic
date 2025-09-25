# AI 에이전트 통합 서비스
import asyncio
import redis
import json
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime
import structlog

from ..agents.base_agent import BaseAgent
from ..agents.data_collection_agent import DataCollectionAgent
from ..agents.data_analysis_agent import DataAnalysisAgent

logger = structlog.get_logger()

class AgentCoordinationService:
    """AI 에이전트 통합 및 조율 서비스"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_client = redis.from_url(redis_url)
        self.agents = {}
        self.is_running = False
        self.coordination_task = None
        
    async def initialize(self):
        """서비스 초기화"""
        try:
            # Redis 연결 테스트
            await self._test_redis_connection()
            
            # AI 에이전트 초기화
            await self._initialize_agents()
            
            # 통합 서비스 시작
            self.is_running = True
            self.coordination_task = asyncio.create_task(self._coordination_loop())
            
            logger.info("Agent coordination service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize agent coordination service: {e}")
            raise
            
    async def _test_redis_connection(self):
        """Redis 연결 테스트"""
        try:
            self.redis_client.ping()
            logger.info("Redis connection successful")
        except Exception as e:
            logger.error(f"Redis connection failed: {e}")
            raise
            
    async def _initialize_agents(self):
        """AI 에이전트 초기화"""
        try:
            # 데이터 수집 에이전트
            self.agents['data_collection'] = DataCollectionAgent(
                agent_id="data_collection",
                redis_url="redis://localhost:6379"
            )
            await self.agents['data_collection'].initialize()
            
            # 데이터 분석 에이전트
            self.agents['data_analysis'] = DataAnalysisAgent(
                agent_id="data_analysis",
                redis_url="redis://localhost:6379"
            )
            await self.agents['data_analysis'].initialize()
            
            logger.info(f"Initialized {len(self.agents)} agents")
            
        except Exception as e:
            logger.error(f"Error initializing agents: {e}")
            raise
            
    async def _coordination_loop(self):
        """에이전트 조율 루프"""
        try:
            while self.is_running:
                # 에이전트 상태 모니터링
                await self._monitor_agent_health()
                
                # 메시지 큐 상태 확인
                await self._monitor_message_queues()
                
                # 에이전트 간 작업 조율
                await self._coordinate_agent_tasks()
                
                await asyncio.sleep(5)  # 5초마다 조율
                
        except asyncio.CancelledError:
            logger.info("Agent coordination loop cancelled")
        except Exception as e:
            logger.error(f"Error in coordination loop: {e}")
            
    async def _monitor_agent_health(self):
        """에이전트 상태 모니터링"""
        try:
            for agent_id, agent in self.agents.items():
                # 에이전트 상태 확인
                if not agent.is_running:
                    logger.warning(f"Agent {agent_id} is not running, attempting restart")
                    await self._restart_agent(agent_id)
                    
        except Exception as e:
            logger.error(f"Error monitoring agent health: {e}")
            
    async def _monitor_message_queues(self):
        """메시지 큐 상태 모니터링"""
        try:
            # Redis Streams 상태 확인
            streams = ['raw-market-data', 'processed-features', 'trading-signals']
            
            for stream in streams:
                # 스트림 길이 확인
                length = self.redis_client.xlen(stream)
                if length > 1000:  # 임계값 초과
                    logger.warning(f"Stream {stream} has {length} pending messages")
                    
        except Exception as e:
            logger.error(f"Error monitoring message queues: {e}")
            
    async def _coordinate_agent_tasks(self):
        """에이전트 간 작업 조율"""
        try:
            # 데이터 수집 작업 시작 (예시)
            if 'data_collection' in self.agents:
                # 실제로는 조건에 따라 작업 시작
                pass
                
        except Exception as e:
            logger.error(f"Error coordinating agent tasks: {e}")
            
    async def _restart_agent(self, agent_id: str):
        """에이전트 재시작"""
        try:
            if agent_id in self.agents:
                agent = self.agents[agent_id]
                
                # 에이전트 중지
                await agent.stop()
                
                # 잠시 대기
                await asyncio.sleep(2)
                
                # 에이전트 재시작
                await agent.start()
                
                logger.info(f"Agent {agent_id} restarted successfully")
                
        except Exception as e:
            logger.error(f"Error restarting agent {agent_id}: {e}")
            
    async def start_data_collection(self, symbols: List[str], exchanges: List[str] = None):
        """데이터 수집 시작"""
        try:
            if 'data_collection' in self.agents:
                agent = self.agents['data_collection']
                await agent.start_collection(symbols, exchanges)
                logger.info(f"Data collection started for {symbols}")
            else:
                logger.error("Data collection agent not available")
                
        except Exception as e:
            logger.error(f"Error starting data collection: {e}")
            raise
            
    async def stop_data_collection(self):
        """데이터 수집 중지"""
        try:
            if 'data_collection' in self.agents:
                agent = self.agents['data_collection']
                await agent.stop_collection()
                logger.info("Data collection stopped")
            else:
                logger.error("Data collection agent not available")
                
        except Exception as e:
            logger.error(f"Error stopping data collection: {e}")
            raise
            
    async def get_system_status(self) -> Dict[str, Any]:
        """시스템 상태 조회"""
        try:
            status = {
                "timestamp": datetime.utcnow().isoformat(),
                "is_running": self.is_running,
                "agents": {},
                "redis_status": "connected",
                "message_queues": {}
            }
            
            # 에이전트 상태
            for agent_id, agent in self.agents.items():
                status["agents"][agent_id] = {
                    "is_running": agent.is_running,
                    "agent_name": agent.agent_name
                }
                
            # 메시지 큐 상태
            streams = ['raw-market-data', 'processed-features', 'trading-signals']
            for stream in streams:
                try:
                    length = self.redis_client.xlen(stream)
                    status["message_queues"][stream] = {
                        "length": length,
                        "status": "healthy" if length < 1000 else "warning"
                    }
                except:
                    status["message_queues"][stream] = {
                        "length": 0,
                        "status": "error"
                    }
                    
            return status
            
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {"error": str(e)}
            
    async def send_message(self, recipient: str, task_name: str, payload: Dict[str, Any]):
        """에이전트에게 메시지 전송"""
        try:
            message = {
                "message_id": str(uuid.uuid4()),
                "correlation_id": str(uuid.uuid4()),
                "timestamp": datetime.utcnow().isoformat(),
                "sender_agent_id": "coordination_service",
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
            
            logger.info(f"Message sent to {recipient}: {task_name}")
            
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            raise
            
    async def stop(self):
        """서비스 중지"""
        try:
            self.is_running = False
            
            # 조율 루프 중지
            if self.coordination_task:
                self.coordination_task.cancel()
                try:
                    await self.coordination_task
                except asyncio.CancelledError:
                    pass
                    
            # 모든 에이전트 중지
            for agent in self.agents.values():
                await agent.stop()
                
            logger.info("Agent coordination service stopped")
            
        except Exception as e:
            logger.error(f"Error stopping coordination service: {e}")
            
    async def cleanup(self):
        """서비스 정리"""
        try:
            await self.stop()
            
            # 에이전트 정리
            for agent in self.agents.values():
                await agent.cleanup()
                
            logger.info("Agent coordination service cleaned up")
            
        except Exception as e:
            logger.error(f"Error cleaning up coordination service: {e}")
