# Stripe 결제 서비스
import stripe
from typing import Optional, Dict, Any
import structlog
from datetime import datetime, timedelta

from app.core.config import settings

# Stripe 설정
stripe.api_key = settings.STRIPE_SECRET_KEY

# 로거 설정
logger = structlog.get_logger()

class PaymentResult:
    """결제 결과 클래스"""
    def __init__(self, success: bool, subscription_id: Optional[str] = None, error: Optional[str] = None):
        self.success = success
        self.subscription_id = subscription_id
        self.error = error

class PaymentService:
    """Stripe 결제 서비스 클래스"""
    
    @staticmethod
    async def create_customer(user_id: str, email: str, name: Optional[str] = None) -> str:
        """Stripe 고객 생성"""
        try:
            customer = stripe.Customer.create(
                email=email,
                name=name,
                metadata={
                    "user_id": user_id
                }
            )
            
            logger.info(
                "Stripe customer created",
                user_id=user_id,
                customer_id=customer.id
            )
            
            return customer.id
            
        except stripe.error.StripeError as e:
            logger.error(
                "Failed to create Stripe customer",
                user_id=user_id,
                error=str(e)
            )
            raise
    
    @staticmethod
    async def create_payment_method(
        customer_id: str,
        payment_method_id: str
    ) -> str:
        """결제 방법 생성"""
        try:
            payment_method = stripe.PaymentMethod.attach(
                payment_method_id,
                customer=customer_id
            )
            
            logger.info(
                "Payment method created",
                customer_id=customer_id,
                payment_method_id=payment_method.id
            )
            
            return payment_method.id
            
        except stripe.error.StripeError as e:
            logger.error(
                "Failed to create payment method",
                customer_id=customer_id,
                error=str(e)
            )
            raise
    
    @staticmethod
    async def create_subscription(
        customer_id: str,
        price_id: str,
        payment_method_id: str,
        trial_days: int = 0
    ) -> PaymentResult:
        """구독 생성"""
        try:
            subscription_params = {
                "customer": customer_id,
                "items": [{"price": price_id}],
                "default_payment_method": payment_method_id,
                "payment_behavior": "default_incomplete",
                "payment_settings": {"save_default_payment_method": "on_subscription"},
                "expand": ["latest_invoice.payment_intent"]
            }
            
            if trial_days > 0:
                subscription_params["trial_period_days"] = trial_days
            
            subscription = stripe.Subscription.create(**subscription_params)
            
            logger.info(
                "Stripe subscription created",
                customer_id=customer_id,
                subscription_id=subscription.id
            )
            
            return PaymentResult(
                success=True,
                subscription_id=subscription.id
            )
            
        except stripe.error.StripeError as e:
            logger.error(
                "Failed to create Stripe subscription",
                customer_id=customer_id,
                error=str(e)
            )
            return PaymentResult(
                success=False,
                error=str(e)
            )
    
    @staticmethod
    async def process_subscription_payment(
        user_id: str,
        payment_method_id: str,
        amount: float
    ) -> PaymentResult:
        """구독 결제 처리"""
        try:
            # 실제 구현에서는 사용자 정보를 데이터베이스에서 조회
            # 여기서는 간단히 처리
            
            # 고객 ID 조회 또는 생성
            customer_id = await PaymentService._get_or_create_customer(user_id)
            
            # 결제 방법 생성
            await PaymentService.create_payment_method(customer_id, payment_method_id)
            
            # 가격 ID 매핑 (실제로는 데이터베이스에서 조회)
            price_id = PaymentService._get_price_id_by_amount(amount)
            
            # 구독 생성
            result = await PaymentService.create_subscription(
                customer_id, price_id, payment_method_id
            )
            
            return result
            
        except Exception as e:
            logger.error(
                "Failed to process subscription payment",
                user_id=user_id,
                error=str(e)
            )
            return PaymentResult(
                success=False,
                error=str(e)
            )
    
    @staticmethod
    async def process_plan_change(
        user_id: str,
        subscription_id: str,
        new_amount: float
    ) -> PaymentResult:
        """플랜 변경 처리"""
        try:
            # 기존 구독 조회
            subscription = stripe.Subscription.retrieve(subscription_id)
            
            # 새 가격 ID 조회
            new_price_id = PaymentService._get_price_id_by_amount(new_amount)
            
            # 구독 업데이트
            updated_subscription = stripe.Subscription.modify(
                subscription_id,
                items=[{
                    "id": subscription["items"]["data"][0]["id"],
                    "price": new_price_id
                }],
                proration_behavior="create_prorations"
            )
            
            logger.info(
                "Subscription plan changed",
                user_id=user_id,
                subscription_id=subscription_id,
                new_amount=new_amount
            )
            
            return PaymentResult(
                success=True,
                subscription_id=updated_subscription.id
            )
            
        except stripe.error.StripeError as e:
            logger.error(
                "Failed to change subscription plan",
                user_id=user_id,
                subscription_id=subscription_id,
                error=str(e)
            )
            return PaymentResult(
                success=False,
                error=str(e)
            )
    
    @staticmethod
    async def cancel_subscription(subscription_id: str) -> bool:
        """구독 취소"""
        try:
            stripe.Subscription.delete(subscription_id)
            
            logger.info(
                "Stripe subscription cancelled",
                subscription_id=subscription_id
            )
            
            return True
            
        except stripe.error.StripeError as e:
            logger.error(
                "Failed to cancel Stripe subscription",
                subscription_id=subscription_id,
                error=str(e)
            )
            return False
    
    @staticmethod
    async def get_subscription(subscription_id: str) -> Optional[Dict[str, Any]]:
        """구독 정보 조회"""
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            
            logger.info(
                "Stripe subscription retrieved",
                subscription_id=subscription_id
            )
            
            return subscription
            
        except stripe.error.StripeError as e:
            logger.error(
                "Failed to retrieve Stripe subscription",
                subscription_id=subscription_id,
                error=str(e)
            )
            return None
    
    @staticmethod
    async def create_payment_intent(
        amount: float,
        currency: str = "usd",
        customer_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """결제 의도 생성"""
        try:
            intent_params = {
                "amount": int(amount * 100),  # 센트 단위로 변환
                "currency": currency,
                "automatic_payment_methods": {
                    "enabled": True
                }
            }
            
            if customer_id:
                intent_params["customer"] = customer_id
            
            payment_intent = stripe.PaymentIntent.create(**intent_params)
            
            logger.info(
                "Payment intent created",
                amount=amount,
                currency=currency,
                intent_id=payment_intent.id
            )
            
            return payment_intent
            
        except stripe.error.StripeError as e:
            logger.error(
                "Failed to create payment intent",
                amount=amount,
                error=str(e)
            )
            return None
    
    @staticmethod
    async def handle_webhook(payload: str, sig_header: str) -> bool:
        """Stripe 웹훅 처리"""
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
            
            # 이벤트 타입별 처리
            if event["type"] == "invoice.payment_succeeded":
                await PaymentService._handle_payment_succeeded(event)
            elif event["type"] == "invoice.payment_failed":
                await PaymentService._handle_payment_failed(event)
            elif event["type"] == "customer.subscription.updated":
                await PaymentService._handle_subscription_updated(event)
            elif event["type"] == "customer.subscription.deleted":
                await PaymentService._handle_subscription_deleted(event)
            
            logger.info(
                "Stripe webhook processed",
                event_type=event["type"],
                event_id=event["id"]
            )
            
            return True
            
        except stripe.error.SignatureVerificationError as e:
            logger.error(
                "Stripe webhook signature verification failed",
                error=str(e)
            )
            return False
        except Exception as e:
            logger.error(
                "Failed to process Stripe webhook",
                error=str(e)
            )
            return False
    
    @staticmethod
    async def _get_or_create_customer(user_id: str) -> str:
        """고객 ID 조회 또는 생성"""
        try:
            # 실제 구현에서는 데이터베이스에서 조회
            # 여기서는 간단히 처리
            customers = stripe.Customer.list(limit=1, email=f"user_{user_id}@example.com")
            
            if customers.data:
                return customers.data[0].id
            else:
                return await PaymentService.create_customer(
                    user_id, f"user_{user_id}@example.com", f"User {user_id}"
                )
                
        except Exception as e:
            logger.error(
                "Failed to get or create customer",
                user_id=user_id,
                error=str(e)
            )
            raise
    
    @staticmethod
    def _get_price_id_by_amount(amount: float) -> str:
        """금액에 따른 가격 ID 조회"""
        # 실제 구현에서는 데이터베이스에서 조회
        # 여기서는 하드코딩된 매핑
        price_mapping = {
            29.99: "price_basic_monthly",
            79.99: "price_premium_monthly",
            199.99: "price_pro_monthly"
        }
        
        return price_mapping.get(amount, "price_basic_monthly")
    
    @staticmethod
    async def _handle_payment_succeeded(event: Dict[str, Any]) -> None:
        """결제 성공 처리"""
        try:
            invoice = event["data"]["object"]
            subscription_id = invoice.get("subscription")
            
            if subscription_id:
                # 구독 상태 업데이트
                logger.info(
                    "Payment succeeded for subscription",
                    subscription_id=subscription_id,
                    amount=invoice["amount_paid"]
                )
                
        except Exception as e:
            logger.error(
                "Failed to handle payment succeeded event",
                error=str(e)
            )
    
    @staticmethod
    async def _handle_payment_failed(event: Dict[str, Any]) -> None:
        """결제 실패 처리"""
        try:
            invoice = event["data"]["object"]
            subscription_id = invoice.get("subscription")
            
            if subscription_id:
                # 구독 상태 업데이트
                logger.info(
                    "Payment failed for subscription",
                    subscription_id=subscription_id,
                    amount=invoice["amount_due"]
                )
                
        except Exception as e:
            logger.error(
                "Failed to handle payment failed event",
                error=str(e)
            )
    
    @staticmethod
    async def _handle_subscription_updated(event: Dict[str, Any]) -> None:
        """구독 업데이트 처리"""
        try:
            subscription = event["data"]["object"]
            subscription_id = subscription["id"]
            
            logger.info(
                "Subscription updated",
                subscription_id=subscription_id,
                status=subscription["status"]
            )
            
        except Exception as e:
            logger.error(
                "Failed to handle subscription updated event",
                error=str(e)
            )
    
    @staticmethod
    async def _handle_subscription_deleted(event: Dict[str, Any]) -> None:
        """구독 삭제 처리"""
        try:
            subscription = event["data"]["object"]
            subscription_id = subscription["id"]
            
            logger.info(
                "Subscription deleted",
                subscription_id=subscription_id
            )
            
        except Exception as e:
            logger.error(
                "Failed to handle subscription deleted event",
                error=str(e)
            )
