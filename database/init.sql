-- Phase 2 데이터베이스 초기화 스크립트

-- 데이터베이스 생성 (이미 존재하는 경우 무시)
-- CREATE DATABASE crypto_trading;

-- 사용자 생성 (이미 존재하는 경우 무시)
-- CREATE USER crypto_user WITH PASSWORD 'crypto_password';

-- 권한 부여
-- GRANT ALL PRIVILEGES ON DATABASE crypto_trading TO crypto_user;

-- 확장 기능 활성화
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- 구독 플랜 초기 데이터 삽입
INSERT INTO subscription_plans (id, name, display_name, description, price_monthly, price_yearly, features, is_active) VALUES
    (uuid_generate_v4(), 'basic', 'Basic', '기본 거래 전략과 모니터링', 29.00, 290.00, 
     '["basic_strategies", "email_support", "basic_dashboard"]', true),
    (uuid_generate_v4(), 'premium', 'Premium', '고급 AI 전략과 분석', 79.00, 790.00, 
     '["all_strategies", "ai_insights", "priority_support", "advanced_dashboard"]', true),
    (uuid_generate_v4(), 'pro', 'Pro', '모든 기능과 API 접근', 199.00, 1990.00, 
     '["all_strategies", "custom_ai", "dedicated_support", "api_access", "custom_dashboard"]', true)
ON CONFLICT (name) DO NOTHING;

-- 기본 관리자 사용자 생성 (개발용)
INSERT INTO users (id, email, password_hash, first_name, last_name, is_active, email_verified, created_at, updated_at) VALUES
    (uuid_generate_v4(), 'admin@crypto-trading.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8KzKz2K', 'Admin', 'User', true, true, NOW(), NOW())
ON CONFLICT (email) DO NOTHING;

-- 인덱스 생성 (성능 최적화)
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);
CREATE INDEX IF NOT EXISTS idx_subscriptions_user_id ON subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_status ON subscriptions(status);
CREATE INDEX IF NOT EXISTS idx_subscriptions_plan_id ON subscriptions(plan_id);
CREATE INDEX IF NOT EXISTS idx_payments_user_id ON payments(user_id);
CREATE INDEX IF NOT EXISTS idx_payments_status ON payments(status);
CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_read ON notifications(is_read);

-- 뷰 생성 (자주 사용되는 쿼리 최적화)
CREATE OR REPLACE VIEW active_subscriptions AS
SELECT 
    s.id,
    s.user_id,
    u.email,
    p.name as plan_name,
    p.display_name as plan_display_name,
    s.status,
    s.current_period_start,
    s.current_period_end,
    s.created_at
FROM subscriptions s
JOIN users u ON s.user_id = u.id
JOIN subscription_plans p ON s.plan_id = p.id
WHERE s.status = 'active';

-- 함수 생성 (비즈니스 로직)
CREATE OR REPLACE FUNCTION get_user_subscription_status(user_email TEXT)
RETURNS TABLE (
    plan_name TEXT,
    status TEXT,
    expires_at TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        p.name,
        s.status,
        s.current_period_end
    FROM users u
    JOIN subscriptions s ON u.id = s.user_id
    JOIN subscription_plans p ON s.plan_id = p.id
    WHERE u.email = user_email
    AND s.status = 'active';
END;
$$ LANGUAGE plpgsql;

-- 트리거 생성 (자동 업데이트)
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- updated_at 자동 업데이트 트리거 적용
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_subscriptions_updated_at BEFORE UPDATE ON subscriptions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_payments_updated_at BEFORE UPDATE ON payments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 데이터베이스 통계 업데이트
ANALYZE;
