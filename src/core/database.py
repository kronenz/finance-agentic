"""
데이터베이스 관리 모듈

거래 기록, 포지션 정보, 성과 데이터 등을 저장하고 관리합니다.
"""

import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from contextlib import contextmanager

from .config import get_config
from .logger import get_logger


class DatabaseManager:
    """데이터베이스 관리자"""
    
    def __init__(self, db_path: Optional[str] = None):
        self.config = get_config()
        self.db_path = db_path or self.config.database.path
        self.logger = get_logger("database")
        self._ensure_database_directory()
        self._initialize_database()
    
    def _ensure_database_directory(self):
        """데이터베이스 디렉토리 생성"""
        db_path = Path(self.db_path)
        db_path.parent.mkdir(parents=True, exist_ok=True)
    
    def _initialize_database(self):
        """데이터베이스 초기화 및 테이블 생성"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 거래 기록 테이블
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    strategy_name TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    side TEXT NOT NULL,  -- 'buy' or 'sell'
                    quantity REAL NOT NULL,
                    price REAL NOT NULL,
                    value REAL NOT NULL,
                    leverage INTEGER DEFAULT 1,
                    pnl REAL DEFAULT 0.0,
                    status TEXT DEFAULT 'open',  -- 'open', 'closed', 'cancelled'
                    close_timestamp DATETIME,
                    close_price REAL,
                    close_pnl REAL,
                    metadata TEXT,  -- JSON 형태의 추가 정보
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 포지션 테이블
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS positions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    strategy_name TEXT NOT NULL,
                    side TEXT NOT NULL,
                    quantity REAL NOT NULL,
                    entry_price REAL NOT NULL,
                    current_price REAL,
                    unrealized_pnl REAL DEFAULT 0.0,
                    leverage INTEGER DEFAULT 1,
                    status TEXT DEFAULT 'open',  -- 'open', 'closed'
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 성과 지표 테이블
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE NOT NULL,
                    strategy_name TEXT NOT NULL,
                    total_trades INTEGER DEFAULT 0,
                    winning_trades INTEGER DEFAULT 0,
                    losing_trades INTEGER DEFAULT 0,
                    total_pnl REAL DEFAULT 0.0,
                    win_rate REAL DEFAULT 0.0,
                    profit_factor REAL DEFAULT 0.0,
                    max_drawdown REAL DEFAULT 0.0,
                    sharpe_ratio REAL DEFAULT 0.0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(date, strategy_name)
                )
            """)
            
            # 시스템 이벤트 테이블
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS system_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    event_type TEXT NOT NULL,  -- 'trade', 'error', 'warning', 'info'
                    message TEXT NOT NULL,
                    data TEXT,  -- JSON 형태의 추가 데이터
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 인덱스 생성
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_trades_timestamp ON trades(timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_trades_strategy ON trades(strategy_name)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_positions_symbol ON positions(symbol)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_positions_strategy ON positions(strategy_name)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_performance_date ON performance_metrics(date)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_timestamp ON system_events(timestamp)")
            
            conn.commit()
            self.logger.info("데이터베이스 초기화 완료")
    
    @contextmanager
    def get_connection(self):
        """데이터베이스 연결 컨텍스트 매니저"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # 딕셔너리 형태로 결과 반환
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            self.logger.error(f"데이터베이스 오류: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def record_trade(self, trade_data: Dict[str, Any]) -> int:
        """거래 기록 저장"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 메타데이터를 JSON 문자열로 변환
            metadata = trade_data.get('metadata', {})
            if isinstance(metadata, dict):
                metadata = json.dumps(metadata, ensure_ascii=False)
            
            cursor.execute("""
                INSERT INTO trades (
                    strategy_name, symbol, side, quantity, price, value,
                    leverage, pnl, status, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                trade_data['strategy_name'],
                trade_data['symbol'],
                trade_data['side'],
                trade_data['quantity'],
                trade_data['price'],
                trade_data['value'],
                trade_data.get('leverage', 1),
                trade_data.get('pnl', 0.0),
                trade_data.get('status', 'open'),
                metadata
            ))
            
            trade_id = cursor.lastrowid
            conn.commit()
            
            self.logger.info(f"거래 기록 저장: ID {trade_id}")
            return trade_id
    
    def update_trade(self, trade_id: int, update_data: Dict[str, Any]) -> bool:
        """거래 기록 업데이트"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            set_clauses = []
            values = []
            
            for key, value in update_data.items():
                if key in ['close_timestamp', 'close_price', 'close_pnl', 'status']:
                    set_clauses.append(f"{key} = ?")
                    values.append(value)
            
            if not set_clauses:
                return False
            
            values.append(trade_id)
            
            cursor.execute(f"""
                UPDATE trades 
                SET {', '.join(set_clauses)}
                WHERE id = ?
            """, values)
            
            conn.commit()
            return cursor.rowcount > 0
    
    def get_open_positions(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """열린 포지션 조회"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if symbol:
                cursor.execute("""
                    SELECT * FROM positions 
                    WHERE status = 'open' AND symbol = ?
                    ORDER BY created_at DESC
                """, (symbol,))
            else:
                cursor.execute("""
                    SELECT * FROM positions 
                    WHERE status = 'open'
                    ORDER BY created_at DESC
                """)
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_trade_history(self, 
                         strategy_name: Optional[str] = None,
                         symbol: Optional[str] = None,
                         start_date: Optional[datetime] = None,
                         end_date: Optional[datetime] = None,
                         limit: int = 100) -> List[Dict[str, Any]]:
        """거래 히스토리 조회"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            where_clauses = []
            params = []
            
            if strategy_name:
                where_clauses.append("strategy_name = ?")
                params.append(strategy_name)
            
            if symbol:
                where_clauses.append("symbol = ?")
                params.append(symbol)
            
            if start_date:
                where_clauses.append("timestamp >= ?")
                params.append(start_date)
            
            if end_date:
                where_clauses.append("timestamp <= ?")
                params.append(end_date)
            
            where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
            
            cursor.execute(f"""
                SELECT * FROM trades 
                {where_sql}
                ORDER BY timestamp DESC
                LIMIT ?
            """, params + [limit])
            
            return [dict(row) for row in cursor.fetchall()]
    
    def calculate_performance_metrics(self, 
                                    strategy_name: str,
                                    start_date: Optional[datetime] = None,
                                    end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """성과 지표 계산"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            where_clauses = ["strategy_name = ?", "status = 'closed'"]
            params = [strategy_name]
            
            if start_date:
                where_clauses.append("close_timestamp >= ?")
                params.append(start_date)
            
            if end_date:
                where_clauses.append("close_timestamp <= ?")
                params.append(end_date)
            
            where_sql = "WHERE " + " AND ".join(where_clauses)
            
            # 기본 통계
            cursor.execute(f"""
                SELECT 
                    COUNT(*) as total_trades,
                    SUM(CASE WHEN close_pnl > 0 THEN 1 ELSE 0 END) as winning_trades,
                    SUM(CASE WHEN close_pnl < 0 THEN 1 ELSE 0 END) as losing_trades,
                    SUM(close_pnl) as total_pnl,
                    AVG(close_pnl) as avg_pnl,
                    MAX(close_pnl) as max_win,
                    MIN(close_pnl) as max_loss
                FROM trades 
                {where_sql}
            """, params)
            
            stats = dict(cursor.fetchone())
            
            # 승률 계산
            if stats['total_trades'] > 0:
                stats['win_rate'] = stats['winning_trades'] / stats['total_trades']
            else:
                stats['win_rate'] = 0.0
            
            # 수익 팩터 계산
            if stats['losing_trades'] > 0:
                total_wins = sum(row['close_pnl'] for row in 
                               cursor.execute(f"SELECT close_pnl FROM trades {where_sql} AND close_pnl > 0", params))
                total_losses = abs(sum(row['close_pnl'] for row in 
                                    cursor.execute(f"SELECT close_pnl FROM trades {where_sql} AND close_pnl < 0", params)))
                stats['profit_factor'] = total_wins / total_losses if total_losses > 0 else 0.0
            else:
                stats['profit_factor'] = float('inf') if stats['total_pnl'] > 0 else 0.0
            
            return stats
    
    def log_system_event(self, event_type: str, message: str, data: Optional[Dict[str, Any]] = None):
        """시스템 이벤트 로깅"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            data_json = json.dumps(data, ensure_ascii=False) if data else None
            
            cursor.execute("""
                INSERT INTO system_events (event_type, message, data)
                VALUES (?, ?, ?)
            """, (event_type, message, data_json))
            
            conn.commit()
    
    def cleanup_old_data(self, days_to_keep: int = 365):
        """오래된 데이터 정리"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            # 오래된 거래 기록 삭제
            cursor.execute("DELETE FROM trades WHERE created_at < ?", (cutoff_date,))
            trades_deleted = cursor.rowcount
            
            # 오래된 시스템 이벤트 삭제
            cursor.execute("DELETE FROM system_events WHERE created_at < ?", (cutoff_date,))
            events_deleted = cursor.rowcount
            
            conn.commit()
            
            self.logger.info(f"데이터 정리 완료: 거래 {trades_deleted}건, 이벤트 {events_deleted}건 삭제")


# 전역 데이터베이스 관리자 인스턴스
db_manager = DatabaseManager()


def get_database() -> DatabaseManager:
    """데이터베이스 관리자 반환"""
    return db_manager
