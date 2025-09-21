# UI/UX 디자인 시스템 명세서

## 개요
**작성자**: AI Agent - UI/UX Designer  
**작성일**: 2024년 12월 19일  
**버전**: 1.0  
**상태**: 🚧 설계 중

## 목적
Phase 2 개인형 구독 서비스를 위한 일관되고 사용자 친화적인 디자인 시스템을 구축하여, 모든 사용자 인터페이스에서 통일된 경험을 제공합니다.

## 디자인 원칙

### 1. 사용자 중심 디자인 (User-Centered Design)
- **사용자 니즈 우선**: 사용자의 요구사항과 목표를 최우선으로 고려
- **직관적 인터페이스**: 학습 없이도 쉽게 사용할 수 있는 인터페이스
- **접근성**: 모든 사용자가 접근 가능한 포용적 디자인
- **일관성**: 모든 화면에서 일관된 디자인 언어 사용

### 2. 브랜드 정체성
- **신뢰성**: 금융 서비스에 적합한 안정적이고 신뢰할 수 있는 느낌
- **전문성**: 전문적인 암호화폐 거래 서비스의 이미지
- **혁신성**: 최신 기술을 활용한 현대적이고 혁신적인 느낌
- **접근성**: 초보자부터 전문가까지 모든 사용자 수준 고려

### 3. 기능성 우선
- **효율성**: 사용자가 목표를 빠르고 효율적으로 달성할 수 있도록
- **명확성**: 정보와 기능이 명확하게 전달되도록
- **단순성**: 복잡한 기능을 단순하고 이해하기 쉽게 표현
- **피드백**: 사용자 행동에 대한 즉각적이고 명확한 피드백

## 색상 시스템

### Primary Colors (주 색상)
```css
/* 메인 브랜드 색상 */
--primary-50: #eff6ff;   /* 매우 연한 파란색 */
--primary-100: #dbeafe;  /* 연한 파란색 */
--primary-200: #bfdbfe;  /* 중간 연한 파란색 */
--primary-300: #93c5fd;  /* 중간 파란색 */
--primary-400: #60a5fa;  /* 중간 진한 파란색 */
--primary-500: #3b82f6;  /* 메인 파란색 */
--primary-600: #2563eb;  /* 진한 파란색 */
--primary-700: #1d4ed8;  /* 매우 진한 파란색 */
--primary-800: #1e40af;  /* 어두운 파란색 */
--primary-900: #1e3a8a;  /* 매우 어두운 파란색 */
```

### Secondary Colors (보조 색상)
```css
/* 성공/긍정적 액션 */
--success-50: #f0fdf4;
--success-100: #dcfce7;
--success-500: #22c55e;
--success-600: #16a34a;
--success-700: #15803d;

/* 경고/주의 */
--warning-50: #fffbeb;
--warning-100: #fef3c7;
--warning-500: #f59e0b;
--warning-600: #d97706;
--warning-700: #b45309;

/* 위험/오류 */
--danger-50: #fef2f2;
--danger-100: #fee2e2;
--danger-500: #ef4444;
--danger-600: #dc2626;
--danger-700: #b91c1c;

/* 정보 */
--info-50: #f0f9ff;
--info-100: #e0f2fe;
--info-500: #06b6d4;
--info-600: #0891b2;
--info-700: #0e7490;
```

### Neutral Colors (중성 색상)
```css
/* 그레이 스케일 */
--gray-50: #f9fafb;
--gray-100: #f3f4f6;
--gray-200: #e5e7eb;
--gray-300: #d1d5db;
--gray-400: #9ca3af;
--gray-500: #6b7280;
--gray-600: #4b5563;
--gray-700: #374151;
--gray-800: #1f2937;
--gray-900: #111827;
```

### Semantic Colors (의미적 색상)
```css
/* 거래 관련 색상 */
--profit: var(--success-500);      /* 수익 */
--loss: var(--danger-500);         /* 손실 */
--neutral: var(--gray-500);        /* 중립 */

/* 상태 색상 */
--active: var(--primary-500);      /* 활성 */
--inactive: var(--gray-400);       /* 비활성 */
--pending: var(--warning-500);     /* 대기 */
--completed: var(--success-500);   /* 완료 */
```

## 타이포그래피

### 폰트 패밀리
```css
/* 메인 폰트 */
--font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;

/* 모노스페이스 폰트 (숫자, 코드) */
--font-mono: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
```

### 폰트 크기
```css
/* 헤딩 */
--text-xs: 0.75rem;     /* 12px */
--text-sm: 0.875rem;    /* 14px */
--text-base: 1rem;      /* 16px */
--text-lg: 1.125rem;    /* 18px */
--text-xl: 1.25rem;     /* 20px */
--text-2xl: 1.5rem;     /* 24px */
--text-3xl: 1.875rem;   /* 30px */
--text-4xl: 2.25rem;    /* 36px */
--text-5xl: 3rem;       /* 48px */
--text-6xl: 3.75rem;    /* 60px */

/* 라인 높이 */
--leading-tight: 1.25;
--leading-snug: 1.375;
--leading-normal: 1.5;
--leading-relaxed: 1.625;
--leading-loose: 2;
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

## 간격 시스템

### 기본 간격
```css
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

## 컴포넌트 디자인

### 1. 버튼 (Button)

#### Primary Button
```css
.btn-primary {
  background-color: var(--primary-500);
  color: white;
  border: none;
  border-radius: 0.5rem;
  padding: 0.75rem 1.5rem;
  font-weight: 500;
  font-size: 0.875rem;
  transition: all 0.2s ease;
}

.btn-primary:hover {
  background-color: var(--primary-600);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
}

.btn-primary:active {
  transform: translateY(0);
  box-shadow: 0 2px 4px rgba(59, 130, 246, 0.4);
}

.btn-primary:disabled {
  background-color: var(--gray-300);
  color: var(--gray-500);
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}
```

#### Secondary Button
```css
.btn-secondary {
  background-color: transparent;
  color: var(--primary-500);
  border: 1px solid var(--primary-500);
  border-radius: 0.5rem;
  padding: 0.75rem 1.5rem;
  font-weight: 500;
  font-size: 0.875rem;
  transition: all 0.2s ease;
}

.btn-secondary:hover {
  background-color: var(--primary-50);
  border-color: var(--primary-600);
  color: var(--primary-600);
}
```

#### Danger Button
```css
.btn-danger {
  background-color: var(--danger-500);
  color: white;
  border: none;
  border-radius: 0.5rem;
  padding: 0.75rem 1.5rem;
  font-weight: 500;
  font-size: 0.875rem;
  transition: all 0.2s ease;
}

.btn-danger:hover {
  background-color: var(--danger-600);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.4);
}
```

### 2. 입력 필드 (Input)

#### 기본 입력 필드
```css
.input {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid var(--gray-300);
  border-radius: 0.5rem;
  font-size: 0.875rem;
  transition: all 0.2s ease;
  background-color: white;
}

.input:focus {
  outline: none;
  border-color: var(--primary-500);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.input:disabled {
  background-color: var(--gray-50);
  color: var(--gray-500);
  cursor: not-allowed;
}

.input.error {
  border-color: var(--danger-500);
}

.input.error:focus {
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
}
```

### 3. 카드 (Card)

#### 기본 카드
```css
.card {
  background-color: white;
  border-radius: 0.75rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border: 1px solid var(--gray-200);
  overflow: hidden;
}

.card-header {
  padding: 1.5rem 1.5rem 0 1.5rem;
  border-bottom: 1px solid var(--gray-200);
}

.card-body {
  padding: 1.5rem;
}

.card-footer {
  padding: 0 1.5rem 1.5rem 1.5rem;
  border-top: 1px solid var(--gray-200);
  background-color: var(--gray-50);
}
```

### 4. 모달 (Modal)

#### 모달 오버레이
```css
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background-color: white;
  border-radius: 0.75rem;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
  max-width: 90vw;
  max-height: 90vh;
  overflow: auto;
}
```

## 레이아웃 시스템

### 그리드 시스템
```css
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

.grid {
  display: grid;
  gap: 1.5rem;
}

.grid-cols-1 { grid-template-columns: repeat(1, minmax(0, 1fr)); }
.grid-cols-2 { grid-template-columns: repeat(2, minmax(0, 1fr)); }
.grid-cols-3 { grid-template-columns: repeat(3, minmax(0, 1fr)); }
.grid-cols-4 { grid-template-columns: repeat(4, minmax(0, 1fr)); }

@media (min-width: 640px) {
  .sm\:grid-cols-2 { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .sm\:grid-cols-3 { grid-template-columns: repeat(3, minmax(0, 1fr)); }
}

@media (min-width: 768px) {
  .md\:grid-cols-3 { grid-template-columns: repeat(3, minmax(0, 1fr)); }
  .md\:grid-cols-4 { grid-template-columns: repeat(4, minmax(0, 1fr)); }
}

@media (min-width: 1024px) {
  .lg\:grid-cols-4 { grid-template-columns: repeat(4, minmax(0, 1fr)); }
  .lg\:grid-cols-6 { grid-template-columns: repeat(6, minmax(0, 1fr)); }
}
```

### 플렉스박스 유틸리티
```css
.flex { display: flex; }
.flex-col { flex-direction: column; }
.flex-row { flex-direction: row; }
.items-center { align-items: center; }
.justify-center { justify-content: center; }
.justify-between { justify-content: space-between; }
.justify-around { justify-content: space-around; }
```

## 아이콘 시스템

### 아이콘 라이브러리
- **Heroicons**: 주요 UI 아이콘
- **Lucide React**: 추가 기능 아이콘
- **Custom Icons**: 브랜드 특화 아이콘

### 아이콘 크기
```css
.icon-xs { width: 0.75rem; height: 0.75rem; }
.icon-sm { width: 1rem; height: 1rem; }
.icon-md { width: 1.25rem; height: 1.25rem; }
.icon-lg { width: 1.5rem; height: 1.5rem; }
.icon-xl { width: 2rem; height: 2rem; }
```

## 애니메이션

### 전환 효과
```css
.transition {
  transition: all 0.2s ease;
}

.transition-fast {
  transition: all 0.1s ease;
}

.transition-slow {
  transition: all 0.3s ease;
}
```

### 호버 효과
```css
.hover-lift:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.hover-scale:hover {
  transform: scale(1.05);
}
```

### 로딩 애니메이션
```css
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
```

## 반응형 디자인

### 브레이크포인트
```css
/* 모바일 */
@media (max-width: 639px) { /* sm */ }

/* 태블릿 */
@media (min-width: 640px) and (max-width: 767px) { /* md */ }

/* 데스크톱 */
@media (min-width: 768px) and (max-width: 1023px) { /* lg */ }

/* 대형 데스크톱 */
@media (min-width: 1024px) { /* xl */ }
```

### 모바일 우선 접근
- 모든 디자인은 모바일부터 시작
- 점진적으로 더 큰 화면에 맞게 확장
- 터치 친화적 인터페이스 설계

## 접근성 (A11y)

### 색상 대비
- **AA 수준**: 4.5:1 이상의 대비율
- **AAA 수준**: 7:1 이상의 대비율 (권장)

### 포커스 관리
```css
.focus-visible:focus {
  outline: 2px solid var(--primary-500);
  outline-offset: 2px;
}
```

### 스크린 리더 지원
- 의미있는 HTML 태그 사용
- ARIA 라벨 제공
- 키보드 네비게이션 지원

## 다크 모드

### 다크 모드 색상
```css
@media (prefers-color-scheme: dark) {
  :root {
    --bg-primary: #111827;
    --bg-secondary: #1f2937;
    --text-primary: #f9fafb;
    --text-secondary: #d1d5db;
    --border-color: #374151;
  }
}
```

## 다음 단계

### 1. 즉시 실행
- [ ] 컴포넌트 라이브러리 구축
- [ ] 스토리북 설정
- [ ] 디자인 토큰 구현
- [ ] 기본 컴포넌트 개발

### 2. 단기 목표 (1주일)
- [ ] 모든 UI 컴포넌트 완성
- [ ] 반응형 디자인 구현
- [ ] 접근성 개선
- [ ] 다크 모드 지원

### 3. 중기 목표 (2주일)
- [ ] 사용자 테스트 실행
- [ ] 피드백 반영
- [ ] 성능 최적화
- [ ] 문서화 완성

## 결론

이 디자인 시스템은 Phase 2 개인형 구독 서비스의 모든 사용자 인터페이스를 일관되고 사용자 친화적으로 만들기 위한 완전한 가이드입니다. 사용자 중심의 디자인 원칙을 바탕으로 접근성, 반응형, 성능을 모두 고려한 현대적인 디자인 시스템을 제공합니다.
