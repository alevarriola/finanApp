import { Suspense } from "react";
import WalletsContent from "@/components/wallets/WalletsContent";

export default function WalletsPage() {
  return (
    <Suspense fallback={<WalletsSkeleton />}>
      <WalletsContent />
    </Suspense>
  );
}

function WalletsSkeleton() {
  return (
    <div className="space-y-4">
      <div className="h-8 w-48 rounded-lg animate-pulse" style={{ backgroundColor: "var(--muted)" }} />
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-32 rounded-xl animate-pulse" style={{ backgroundColor: "var(--muted)" }} />
        ))}
      </div>
    </div>
  );
}
