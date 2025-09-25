// 스켈레톤 로더 컴포넌트
import React from 'react';

interface SkeletonLoaderProps {
  className?: string;
  height?: string;
  width?: string;
  rounded?: boolean;
}

const SkeletonLoader: React.FC<SkeletonLoaderProps> = ({
  className = '',
  height = 'h-4',
  width = 'w-full',
  rounded = true,
}) => {
  return (
    <div
      className={`${height} ${width} ${
        rounded ? 'rounded' : ''
      } bg-gray-200 animate-pulse ${className}`}
    />
  );
};

// 구독 플랜 카드용 스켈레톤
export const SubscriptionPlanSkeleton: React.FC = () => {
  return (
    <div className="bg-white rounded-lg shadow-lg border-2 border-gray-200 p-6 animate-pulse">
      <div className="text-center">
        {/* 플랜 이름 */}
        <SkeletonLoader height="h-6" width="w-24" className="mx-auto mb-2" />
        
        {/* 플랜 설명 */}
        <SkeletonLoader height="h-4" width="w-32" className="mx-auto mb-4" />
        
        {/* 가격 */}
        <SkeletonLoader height="h-8" width="w-20" className="mx-auto mb-6" />
        
        {/* 기능 목록 */}
        <div className="space-y-3 mb-6">
          {[...Array(4)].map((_, index) => (
            <div key={index} className="flex items-center">
              <SkeletonLoader height="h-5" width="w-5" className="mr-3 rounded-full" />
              <SkeletonLoader height="h-4" width="w-32" />
            </div>
          ))}
        </div>
        
        {/* 버튼 */}
        <SkeletonLoader height="h-12" width="w-full" className="rounded-lg" />
      </div>
    </div>
  );
};

// 구독 관리 카드용 스켈레톤
export const SubscriptionManagementSkeleton: React.FC = () => {
  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow-lg p-6 animate-pulse">
        {/* 헤더 */}
        <div className="flex justify-between items-start mb-6">
          <div>
            <SkeletonLoader height="h-8" width="w-32" className="mb-2" />
            <SkeletonLoader height="h-4" width="w-24" />
          </div>
          <SkeletonLoader height="h-6" width="w-16" className="rounded-full" />
        </div>

        {/* 구독 세부사항 */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div>
            <SkeletonLoader height="h-6" width="w-32" className="mb-4" />
            <div className="space-y-2">
              {[...Array(4)].map((_, index) => (
                <div key={index} className="flex justify-between">
                  <SkeletonLoader height="h-4" width="w-20" />
                  <SkeletonLoader height="h-4" width="w-24" />
                </div>
              ))}
            </div>
          </div>

          <div>
            <SkeletonLoader height="h-6" width="w-16" className="mb-4" />
            <div className="space-y-3">
              <SkeletonLoader height="h-10" width="w-full" className="rounded" />
              <SkeletonLoader height="h-10" width="w-full" className="rounded" />
            </div>
          </div>
        </div>

        {/* 구독 이력 */}
        <div className="border-t pt-6">
          <SkeletonLoader height="h-6" width="w-32" className="mb-4" />
          <SkeletonLoader height="h-4" width="w-24" />
        </div>
      </div>
    </div>
  );
};

export default SkeletonLoader;
