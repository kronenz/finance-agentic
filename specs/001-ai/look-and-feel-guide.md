# Look & Feel Guide: AI 기반 암호화폐 거래 시스템

**Version**: 1.0.0  
**Date**: 2024-12-19  
**Design System**: Modern Financial Dashboard

## 디자인 철학

### 핵심 원칙
1. **정보 밀도 최적화**: 복잡한 금융 데이터를 직관적으로 표현
2. **실시간 반응성**: 데이터 변화에 즉각적인 시각적 피드백
3. **신뢰성**: 금융 서비스에 적합한 안정적이고 전문적인 디자인
4. **접근성**: 모든 사용자가 동등하게 접근 가능한 인터페이스
5. **확장성**: 새로운 기능 추가 시 일관성 유지

### 디자인 방향성
- **미니멀리즘**: 불필요한 요소 제거, 핵심 정보에 집중
- **데이터 중심**: 시각적 요소보다 데이터 가독성 우선
- **다크 모드**: 24시간 거래 환경에 적합한 다크 테마
- **모바일 퍼스트**: 다양한 디바이스에서 일관된 경험

## 색상 시스템

### Primary Colors
```css
/* 메인 브랜드 컬러 - 신뢰감과 안정성 */
--primary-50: #eff6ff;   /* 매우 연한 파란색 */
--primary-100: #dbeafe;  /* 연한 파란색 */
--primary-200: #bfdbfe;  /* 밝은 파란색 */
--primary-300: #93c5fd;  /* 중간 파란색 */
--primary-400: #60a5fa;  /* 진한 파란색 */
--primary-500: #3b82f6;  /* 메인 파란색 */
--primary-600: #2563eb;  /* 진한 파란색 */
--primary-700: #1d4ed8;  /* 매우 진한 파란색 */
--primary-800: #1e40af;  /* 어두운 파란색 */
--primary-900: #1e3a8a;  /* 가장 어두운 파란색 */
```

### Semantic Colors
```css
/* 성공/수익 - 긍정적 신호 */
--success-50: #f0fdf4;
--success-100: #dcfce7;
--success-500: #22c55e;  /* 메인 녹색 */
--success-600: #16a34a;
--success-700: #15803d;

/* 위험/손실 - 부정적 신호 */
--danger-50: #fef2f2;
--danger-100: #fee2e2;
--danger-500: #ef4444;   /* 메인 빨간색 */
--danger-600: #dc2626;
--danger-700: #b91c1c;

/* 경고/주의 - 중립적 신호 */
--warning-50: #fffbeb;
--warning-100: #fef3c7;
--warning-500: #f59e0b;  /* 메인 주황색 */
--warning-600: #d97706;
--warning-700: #b45309;

/* 정보/중립 - 일반 정보 */
--info-50: #f0f9ff;
--info-100: #e0f2fe;
--info-500: #06b6d4;     /* 메인 청록색 */
--info-600: #0891b2;
--info-700: #0e7490;
```

### Neutral Colors
```css
/* 중성 색상 - 텍스트 및 배경 */
--neutral-50: #fafafa;   /* 가장 밝은 회색 */
--neutral-100: #f5f5f5;  /* 밝은 회색 */
--neutral-200: #e5e5e5;  /* 연한 회색 */
--neutral-300: #d4d4d4;  /* 중간 연한 회색 */
--neutral-400: #a3a3a3;  /* 중간 회색 */
--neutral-500: #737373;  /* 중간 진한 회색 */
--neutral-600: #525252;  /* 진한 회색 */
--neutral-700: #404040;  /* 매우 진한 회색 */
--neutral-800: #262626;  /* 어두운 회색 */
--neutral-900: #171717;  /* 가장 어두운 회색 */
```

### 다크 모드 색상
```css
[data-theme="dark"] {
  /* 다크 모드에서는 색상 값이 반전 */
  --neutral-50: #171717;
  --neutral-100: #262626;
  --neutral-200: #404040;
  --neutral-300: #525252;
  --neutral-400: #737373;
  --neutral-500: #a3a3a3;
  --neutral-600: #d4d4d4;
  --neutral-700: #e5e5e5;
  --neutral-800: #f5f5f5;
  --neutral-900: #fafafa;
}
```

## 타이포그래피

### 폰트 패밀리
```css
/* 메인 폰트 - Inter (가독성 최적화) */
--font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;

/* 모노스페이스 폰트 - 숫자 및 코드 */
--font-mono: 'JetBrains Mono', 'Fira Code', 'Monaco', 'Consolas', 'Courier New', monospace;
```

### 폰트 크기 시스템
```css
/* 제목 크기 */
--text-xs: 0.75rem;     /* 12px - 작은 라벨 */
--text-sm: 0.875rem;    /* 14px - 본문 텍스트 */
--text-base: 1rem;      /* 16px - 기본 크기 */
--text-lg: 1.125rem;    /* 18px - 큰 본문 */
--text-xl: 1.25rem;     /* 20px - 작은 제목 */
--text-2xl: 1.5rem;     /* 24px - 중간 제목 */
--text-3xl: 1.875rem;   /* 30px - 큰 제목 */
--text-4xl: 2.25rem;    /* 36px - 매우 큰 제목 */
--text-5xl: 3rem;       /* 48px - 헤로 제목 */
```

### 폰트 가중치
```css
--font-thin: 100;
--font-light: 300;
--font-normal: 400;
--font-medium: 500;
--font-semibold: 600;
--font-bold: 700;
--font-extrabold: 800;
--font-black: 900;
```

### 라인 높이
```css
--leading-tight: 1.25;    /* 제목용 */
--leading-snug: 1.375;    /* 부제목용 */
--leading-normal: 1.5;    /* 본문용 */
--leading-relaxed: 1.625; /* 긴 본문용 */
--leading-loose: 2;       /* 넓은 간격용 */
```

## 간격 시스템

### 기본 간격 단위
```css
/* 4px 기반 간격 시스템 */
--space-0: 0;
--space-1: 0.25rem;   /* 4px */
--space-2: 0.5rem;    /* 8px */
--space-3: 0.75rem;   /* 12px */
--space-4: 1rem;      /* 16px */
--space-5: 1.25rem;   /* 20px */
--space-6: 1.5rem;    /* 24px */
--space-8: 2rem;      /* 32px */
--space-10: 2.5rem;   /* 40px */
--space-12: 3rem;     /* 48px */
--space-16: 4rem;     /* 64px */
--space-20: 5rem;     /* 80px */
--space-24: 6rem;     /* 96px */
--space-32: 8rem;     /* 128px */
```

### 패딩 및 마진
```css
/* 패딩 */
--p-0: 0;
--p-1: var(--space-1);
--p-2: var(--space-2);
--p-3: var(--space-3);
--p-4: var(--space-4);
--p-6: var(--space-6);
--p-8: var(--space-8);

/* 마진 */
--m-0: 0;
--m-1: var(--space-1);
--m-2: var(--space-2);
--m-3: var(--space-3);
--m-4: var(--space-4);
--m-6: var(--space-6);
--m-8: var(--space-8);
```

## 그림자 시스템

### 그림자 레벨
```css
/* 작은 그림자 - 카드, 버튼 */
--shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);

/* 중간 그림자 - 모달, 드롭다운 */
--shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);

/* 큰 그림자 - 팝오버, 툴팁 */
--shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);

/* 매우 큰 그림자 - 모달 배경 */
--shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);

/* 극대 그림자 - 특별한 강조 */
--shadow-2xl: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
```

## 둥근 모서리

### 반경 시스템
```css
--radius-none: 0;
--radius-sm: 0.125rem;   /* 2px - 작은 요소 */
--radius-md: 0.375rem;   /* 6px - 기본 요소 */
--radius-lg: 0.5rem;     /* 8px - 큰 요소 */
--radius-xl: 0.75rem;    /* 12px - 매우 큰 요소 */
--radius-2xl: 1rem;      /* 16px - 특별한 요소 */
--radius-3xl: 1.5rem;    /* 24px - 극대 요소 */
--radius-full: 9999px;   /* 완전한 원형 */
```

## 애니메이션

### 전환 시간
```css
--transition-none: none;
--transition-all: all 150ms cubic-bezier(0.4, 0, 0.2, 1);
--transition-fast: 150ms ease-in-out;
--transition-normal: 300ms ease-in-out;
--transition-slow: 500ms ease-in-out;
```

### 이징 함수
```css
--ease-linear: linear;
--ease-in: cubic-bezier(0.4, 0, 1, 1);
--ease-out: cubic-bezier(0, 0, 0.2, 1);
--ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
```

### 애니메이션 키프레임
```css
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideInUp {
  from { transform: translateY(100%); }
  to { transform: translateY(0); }
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
```

## 컴포넌트 스타일 가이드

### 버튼 스타일
```css
/* Primary Button */
.btn-primary {
  background: var(--primary-500);
  color: white;
  padding: var(--space-3) var(--space-6);
  border-radius: var(--radius-md);
  font-weight: var(--font-medium);
  transition: var(--transition-fast);
  box-shadow: var(--shadow-sm);
}

.btn-primary:hover {
  background: var(--primary-600);
  box-shadow: var(--shadow-md);
}

.btn-primary:active {
  background: var(--primary-700);
  transform: translateY(1px);
}

/* Success Button (거래 신호용) */
.btn-success {
  background: var(--success-500);
  color: white;
  /* ... 동일한 패턴 ... */
}

/* Danger Button (리스크 알림용) */
.btn-danger {
  background: var(--danger-500);
  color: white;
  /* ... 동일한 패턴 ... */
}
```

### 카드 스타일
```css
.card {
  background: var(--neutral-50);
  border: 1px solid var(--neutral-200);
  border-radius: var(--radius-lg);
  padding: var(--space-6);
  box-shadow: var(--shadow-sm);
  transition: var(--transition-fast);
}

.card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.card-header {
  border-bottom: 1px solid var(--neutral-200);
  padding-bottom: var(--space-4);
  margin-bottom: var(--space-4);
}

.card-title {
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  color: var(--neutral-900);
  margin: 0;
}
```

### 입력 필드 스타일
```css
.input {
  width: 100%;
  padding: var(--space-3) var(--space-4);
  border: 1px solid var(--neutral-300);
  border-radius: var(--radius-md);
  font-size: var(--text-base);
  transition: var(--transition-fast);
  background: var(--neutral-50);
}

.input:focus {
  outline: none;
  border-color: var(--primary-500);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.input:invalid {
  border-color: var(--danger-500);
}

.input::placeholder {
  color: var(--neutral-400);
}
```

## 차트 및 데이터 시각화

### 차트 색상 팔레트
```css
/* 차트용 색상 */
--chart-1: #3b82f6;  /* 파란색 */
--chart-2: #22c55e;  /* 녹색 */
--chart-3: #ef4444;  /* 빨간색 */
--chart-4: #f59e0b;  /* 주황색 */
--chart-5: #8b5cf6;  /* 보라색 */
--chart-6: #06b6d4;  /* 청록색 */
--chart-7: #84cc16;  /* 라임색 */
--chart-8: #f97316;  /* 오렌지색 */
```

### 차트 그리드 및 축
```css
.chart-grid {
  stroke: var(--neutral-200);
  stroke-width: 1px;
  opacity: 0.5;
}

.chart-axis {
  stroke: var(--neutral-400);
  stroke-width: 1px;
}

.chart-text {
  fill: var(--neutral-600);
  font-size: var(--text-sm);
  font-family: var(--font-sans);
}
```

## 반응형 디자인

### 브레이크포인트
```css
/* Mobile First 접근법 */
@media (min-width: 640px) {  /* sm */ }
@media (min-width: 768px) {  /* md */ }
@media (min-width: 1024px) { /* lg */ }
@media (min-width: 1280px) { /* xl */ }
@media (min-width: 1536px) { /* 2xl */ }
```

### 그리드 시스템
```css
.container {
  width: 100%;
  margin: 0 auto;
  padding: 0 var(--space-4);
}

@media (min-width: 640px) {
  .container { max-width: 640px; }
}

@media (min-width: 768px) {
  .container { max-width: 768px; }
}

@media (min-width: 1024px) {
  .container { max-width: 1024px; }
}

@media (min-width: 1280px) {
  .container { max-width: 1280px; }
}
```

## 접근성 가이드라인

### 색상 대비
- **일반 텍스트**: 최소 4.5:1 대비율
- **큰 텍스트**: 최소 3:1 대비율
- **UI 컴포넌트**: 최소 3:1 대비율

### 포커스 표시
```css
.focus-visible {
  outline: 2px solid var(--primary-500);
  outline-offset: 2px;
}
```

### 스크린 리더 지원
```css
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
```

## 다크 모드 지원

### 다크 모드 변수
```css
[data-theme="dark"] {
  /* 배경색 */
  --bg-primary: var(--neutral-900);
  --bg-secondary: var(--neutral-800);
  --bg-tertiary: var(--neutral-700);
  
  /* 텍스트 색상 */
  --text-primary: var(--neutral-100);
  --text-secondary: var(--neutral-300);
  --text-tertiary: var(--neutral-400);
  
  /* 테두리 */
  --border-primary: var(--neutral-700);
  --border-secondary: var(--neutral-600);
}
```

### 다크 모드 전환
```css
.theme-transition {
  transition: background-color 300ms ease-in-out,
              color 300ms ease-in-out,
              border-color 300ms ease-in-out;
}
```

## 성능 최적화

### CSS 최적화
```css
/* GPU 가속 */
.gpu-accelerated {
  transform: translateZ(0);
  will-change: transform;
}

/* 레이아웃 최적화 */
.optimized-layout {
  contain: layout style paint;
}

/* 애니메이션 최적화 */
.optimized-animation {
  transform: translateZ(0);
  backface-visibility: hidden;
  perspective: 1000px;
}
```

## 결론

이 Look & Feel 가이드는 AI 기반 암호화폐 거래 시스템의 시각적 일관성과 사용자 경험을 보장합니다. 모든 디자인 요소는 금융 서비스의 신뢰성과 전문성을 반영하면서도, 현대적이고 직관적인 인터페이스를 제공하도록 설계되었습니다.

디자인 시스템은 확장 가능하고 유지보수가 용이하도록 구성되어 있으며, 팀의 모든 구성원이 일관된 디자인을 구현할 수 있도록 지원합니다.
