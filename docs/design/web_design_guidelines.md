# 웹 디자인 가이드라인 스펙

## 📋 개요
Crypto Trading Subscription Service의 웹 디자인 가이드라인입니다. Apple 홈페이지 스타일을 기반으로 한 일관성 있는 사용자 경험을 제공합니다.

## 🎨 디자인 시스템

### 1. 색상 팔레트 (Color Palette)

#### Primary Colors
- **Primary Blue**: `#007AFF` - 메인 액션 버튼, 링크
- **Primary Blue Dark**: `#0056CC` - 호버 상태
- **Primary Blue Light**: `#4DA6FF` - 비활성 상태

#### Secondary Colors
- **Gray 900**: `#1C1C1E` - 메인 텍스트
- **Gray 800**: `#2C2C2E` - 서브 텍스트
- **Gray 700**: `#3A3A3C` - 플레이스홀더
- **Gray 600**: `#48484A` - 보조 텍스트
- **Gray 500**: `#636366` - 비활성 텍스트
- **Gray 400**: `#8E8E93` - 경계선
- **Gray 300**: `#C7C7CC` - 구분선
- **Gray 200**: `#E5E5EA` - 배경
- **Gray 100**: `#F2F2F7` - 카드 배경

#### Status Colors
- **Success Green**: `#34C759` - 성공 메시지
- **Warning Orange**: `#FF9500` - 경고 메시지
- **Error Red**: `#FF3B30` - 오류 메시지
- **Info Blue**: `#007AFF` - 정보 메시지

#### Background Colors
- **White**: `#FFFFFF` - 메인 배경
- **Black**: `#000000` - 텍스트
- **Transparent**: `rgba(0, 0, 0, 0)` - 투명

### 2. 타이포그래피 (Typography)

#### Font Family
- **Primary**: `-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif`
- **Monospace**: `'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', monospace`

#### Font Sizes
- **Display Large**: `48px` / `3rem` - 메인 헤드라인
- **Display Medium**: `36px` / `2.25rem` - 섹션 헤드라인
- **Display Small**: `28px` / `1.75rem` - 카드 헤드라인
- **Headline**: `24px` / `1.5rem` - 페이지 제목
- **Title**: `20px` / `1.25rem` - 섹션 제목
- **Body Large**: `18px` / `1.125rem` - 본문 텍스트
- **Body**: `16px` / `1rem` - 기본 텍스트
- **Body Small**: `14px` / `0.875rem` - 보조 텍스트
- **Caption**: `12px` / `0.75rem` - 캡션
- **Caption Small**: `10px` / `0.625rem` - 작은 캡션

#### Font Weights
- **Light**: `300`
- **Regular**: `400`
- **Medium**: `500`
- **Semibold**: `600`
- **Bold**: `700`
- **Heavy**: `800`

#### Line Heights
- **Tight**: `1.2`
- **Normal**: `1.4`
- **Relaxed**: `1.6`
- **Loose**: `1.8`

### 3. 간격 시스템 (Spacing System)

#### Base Unit: 4px
- **xs**: `4px` / `0.25rem`
- **sm**: `8px` / `0.5rem`
- **md**: `12px` / `0.75rem`
- **lg**: `16px` / `1rem`
- **xl**: `20px` / `1.25rem`
- **2xl**: `24px` / `1.5rem`
- **3xl**: `32px` / `2rem`
- **4xl**: `40px` / `2.5rem`
- **5xl**: `48px` / `3rem`
- **6xl**: `64px` / `4rem`

### 4. 그림자 시스템 (Shadow System)

#### Shadow Levels
- **xs**: `0 1px 2px rgba(0, 0, 0, 0.05)`
- **sm**: `0 1px 3px rgba(0, 0, 0, 0.1), 0 1px 2px rgba(0, 0, 0, 0.06)`
- **md**: `0 4px 6px rgba(0, 0, 0, 0.07), 0 2px 4px rgba(0, 0, 0, 0.06)`
- **lg**: `0 10px 15px rgba(0, 0, 0, 0.1), 0 4px 6px rgba(0, 0, 0, 0.05)`
- **xl**: `0 20px 25px rgba(0, 0, 0, 0.1), 0 10px 10px rgba(0, 0, 0, 0.04)`
- **2xl**: `0 25px 50px rgba(0, 0, 0, 0.25)`

### 5. 아이콘 시스템 (Icon System)

#### Icon Sizes
- **xs**: `12px` / `0.75rem` - 작은 아이콘
- **sm**: `14px` / `0.875rem` - 작은 아이콘
- **md**: `16px` / `1rem` - 기본 아이콘
- **lg**: `20px` / `1.25rem` - 큰 아이콘
- **xl**: `24px` / `1.5rem` - 매우 큰 아이콘
- **2xl**: `32px` / `2rem` - 헤더 아이콘

#### Icon Guidelines
- **일관성**: 모든 아이콘은 동일한 스타일 가이드라인을 따름
- **크기**: 텍스트와의 비율을 고려하여 적절한 크기 사용
- **색상**: 텍스트 색상과 일치하거나 의미에 맞는 색상 사용
- **간격**: 아이콘과 텍스트 사이에 적절한 간격 유지

### 6. 버튼 시스템 (Button System)

#### Button Sizes
- **Small**: `height: 32px, padding: 0 12px, font-size: 14px`
- **Medium**: `height: 40px, padding: 0 16px, font-size: 16px`
- **Large**: `height: 48px, padding: 0 20px, font-size: 18px`

#### Button Variants
- **Primary**: 파란색 배경, 흰색 텍스트
- **Secondary**: 회색 배경, 어두운 텍스트
- **Outline**: 투명 배경, 파란색 테두리
- **Ghost**: 투명 배경, 파란색 텍스트
- **Danger**: 빨간색 배경, 흰색 텍스트

### 7. 입력 필드 시스템 (Input System)

#### Input Sizes
- **Small**: `height: 32px, padding: 0 12px`
- **Medium**: `height: 40px, padding: 0 16px`
- **Large**: `height: 48px, padding: 0 20px`

#### Input States
- **Default**: 회색 테두리
- **Focus**: 파란색 테두리, 그림자 효과
- **Error**: 빨간색 테두리, 오류 메시지
- **Success**: 초록색 테두리
- **Disabled**: 회색 배경, 비활성화

### 8. 카드 시스템 (Card System)

#### Card Variants
- **Default**: 흰색 배경, 회색 테두리
- **Elevated**: 그림자 효과
- **Outlined**: 테두리만 있는 카드
- **Filled**: 회색 배경

#### Card Padding
- **Small**: `16px`
- **Medium**: `24px`
- **Large**: `32px`

### 9. 애니메이션 시스템 (Animation System)

#### Animation Durations
- **Fast**: `150ms`
- **Normal**: `300ms`
- **Slow**: `500ms`

#### Animation Easing
- **Ease In**: `cubic-bezier(0.4, 0, 1, 1)`
- **Ease Out**: `cubic-bezier(0, 0, 0.2, 1)`
- **Ease In Out**: `cubic-bezier(0.4, 0, 0.2, 1)`

#### Common Animations
- **Fade In**: 투명도 0에서 1로
- **Slide Up**: 아래에서 위로 이동
- **Scale In**: 크기 0.95에서 1로
- **Shake**: 좌우로 흔들림 (오류 시)

### 10. 반응형 디자인 (Responsive Design)

#### Breakpoints
- **Mobile**: `320px - 767px`
- **Tablet**: `768px - 1023px`
- **Desktop**: `1024px - 1439px`
- **Large Desktop**: `1440px+`

#### Grid System
- **Mobile**: 1열 그리드
- **Tablet**: 2열 그리드
- **Desktop**: 3-4열 그리드
- **Large Desktop**: 4-6열 그리드

### 11. 접근성 (Accessibility)

#### Color Contrast
- **Normal Text**: 최소 4.5:1 비율
- **Large Text**: 최소 3:1 비율
- **UI Components**: 최소 3:1 비율

#### Focus States
- **Visible Focus**: 모든 인터랙티브 요소에 포커스 표시
- **Keyboard Navigation**: 키보드만으로 모든 기능 접근 가능

#### Screen Reader Support
- **Semantic HTML**: 의미있는 HTML 태그 사용
- **ARIA Labels**: 적절한 ARIA 라벨 제공
- **Alt Text**: 모든 이미지에 대체 텍스트 제공

### 12. 컴포넌트 가이드라인

#### Form Components
- **Label**: 명확하고 간결한 라벨
- **Placeholder**: 도움말 텍스트로 사용
- **Error Message**: 구체적이고 도움이 되는 오류 메시지
- **Success Message**: 긍정적인 피드백 제공

#### Navigation Components
- **Breadcrumb**: 현재 위치 표시
- **Pagination**: 페이지 네비게이션
- **Tabs**: 관련 콘텐츠 그룹화

#### Feedback Components
- **Alert**: 중요한 메시지 표시
- **Toast**: 일시적인 알림
- **Modal**: 중요한 작업 확인
- **Tooltip**: 추가 정보 제공

## 🛠️ 구현 가이드

### CSS 클래스 명명 규칙
- **Prefix**: `apple-` 접두사 사용
- **Component**: 컴포넌트 이름 (예: `button`, `input`, `card`)
- **Variant**: 변형 이름 (예: `primary`, `secondary`, `large`)
- **State**: 상태 이름 (예: `hover`, `active`, `disabled`)

### 예시
```css
.apple-btn-primary { /* 기본 버튼 */ }
.apple-btn-primary:hover { /* 호버 상태 */ }
.apple-btn-primary:disabled { /* 비활성 상태 */ }
.apple-input-field { /* 입력 필드 */ }
.apple-input-field:focus { /* 포커스 상태 */ }
.apple-input-field.error { /* 오류 상태 */ }
```

## 📱 모바일 최적화

### Touch Targets
- **최소 크기**: 44px x 44px
- **간격**: 터치 타겟 사이 최소 8px 간격

### Gestures
- **Swipe**: 좌우 스와이프 지원
- **Pinch**: 확대/축소 지원
- **Pull to Refresh**: 새로고침 제스처

## 🎯 성능 최적화

### 이미지 최적화
- **WebP 형식** 사용
- **Lazy Loading** 구현
- **적절한 크기**로 리사이징

### CSS 최적화
- **Critical CSS** 인라인
- **미사용 CSS** 제거
- **CSS 압축** 적용

### JavaScript 최적화
- **Code Splitting** 적용
- **Tree Shaking** 사용
- **번들 크기** 최적화

## 📊 품질 보증

### 디자인 리뷰 체크리스트
- [ ] 색상 대비 비율 확인
- [ ] 일관된 간격 사용
- [ ] 적절한 타이포그래피 계층
- [ ] 반응형 디자인 테스트
- [ ] 접근성 가이드라인 준수
- [ ] 브라우저 호환성 확인

### 테스트 환경
- **Chrome**: 최신 버전
- **Firefox**: 최신 버전
- **Safari**: 최신 버전
- **Edge**: 최신 버전
- **Mobile Safari**: iOS 최신 버전
- **Chrome Mobile**: Android 최신 버전

---

**마지막 업데이트**: 2025-09-22
**버전**: 1.0.0
**담당자**: UI/UX Designer
