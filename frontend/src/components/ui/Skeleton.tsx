/**
 * Skeleton Component - Placeholder de chargement
 */
interface SkeletonProps {
  className?: string;
}

export default function Skeleton({ className = '' }: SkeletonProps) {
  return (
    <div 
      className={`animate-pulse bg-slate-700 rounded ${className}`}
    />
  );
}

export function MatchCardSkeleton() {
  return (
    <div className="bg-slate-800/50 rounded-xl border border-slate-700 p-4">
      <div className="flex justify-between items-center mb-3">
        <Skeleton className="h-5 w-12" />
        <Skeleton className="h-4 w-24" />
      </div>
      <div className="flex items-center justify-between gap-4">
        <Skeleton className="h-6 w-32" />
        <Skeleton className="h-8 w-20" />
        <Skeleton className="h-6 w-32" />
      </div>
    </div>
  );
}

export function StandingsTableSkeleton() {
  return (
    <div className="space-y-2">
      {[...Array(10)].map((_, i) => (
        <div key={i} className="flex items-center gap-4 p-3">
          <Skeleton className="h-5 w-8" />
          <Skeleton className="h-6 w-6 rounded-full" />
          <Skeleton className="h-5 w-40" />
          <div className="ml-auto flex gap-4">
            {[...Array(8)].map((_, j) => (
              <Skeleton key={j} className="h-5 w-8" />
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
