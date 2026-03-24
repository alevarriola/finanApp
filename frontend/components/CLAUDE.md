# Components — Guide for Claude Agents

## Organization

```
components/
├── shared/          # Reusable across the whole app
├── ui/              # Wrapped Radix UI primitives
├── hooks/           # React Query custom hooks
├── lib/
│   ├── graphql/     # GraphQL client
│   └── toast.ts     # Toast helpers
├── providers/       # Context providers
└── [module]/        # Domain-specific components
    ├── WalletsContent.tsx
    ├── WalletCard.tsx
    └── CreateWalletModal.tsx
```

## Hook Pattern (React Query)

```typescript
// hooks/useWallets.ts
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { graphqlRequest } from "@/components/lib/graphql/client";

const GET_WALLETS = `
    query GetWallets {
        listWallets {
            id name balance currency createdAt
        }
    }
`;

export function useWallets() {
    return useQuery({
        queryKey: ["wallets"],
        queryFn: () => graphqlRequest<{ listWallets: Wallet[] }>({ query: GET_WALLETS }),
        staleTime: 30_000,
    });
}

export function useCreateWallet() {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: (input: CreateWalletInput) =>
            graphqlRequest({ query: CREATE_WALLET, variables: { input } }),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["wallets"] });
        },
    });
}
```

## Content Component Pattern

```tsx
// wallets/WalletsContent.tsx
"use client";
import { useWallets } from "@/components/hooks/useWallets";

export default function WalletsContent() {
    const { data, isLoading, isError } = useWallets();

    if (isLoading) return <LoadingSkeleton />;
    if (isError) return <ErrorDisplay />;

    return (
        <div className="space-y-4">
            {/* content */}
        </div>
    );
}
```

## Modal with Form Pattern

```tsx
// wallets/CreateWalletModal.tsx
"use client";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { toast } from "sonner";
import { useCreateWallet } from "@/components/hooks/useWallets";

const schema = z.object({
    name: z.string().min(1, "Name is required"),
    initialBalance: z.number().min(0),
});

export function CreateWalletModal({ isOpen, onClose }: Props) {
    const { mutate, isPending } = useCreateWallet();
    const form = useForm({ resolver: zodResolver(schema) });

    const onSubmit = (data: z.infer<typeof schema>) => {
        mutate(data, {
            onSuccess: () => { toast.success("Wallet created!"); onClose(); },
            onError: () => toast.error("Failed to create wallet"),
        });
    };

    // Radix UI Dialog...
}
```

## GraphQL Client (`lib/graphql/client.ts`)

```typescript
export async function graphqlRequest<T>(options: {
    query: string;
    variables?: Record<string, unknown>;
}): Promise<T> {
    const res = await fetch("/api/backend", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(options),
    });
    const json = await res.json();
    if (json.errors) throw new Error(json.errors[0].message);
    return json.data as T;
}
```

## Toast Helpers (`lib/toast.ts`)

```typescript
import { toast } from "sonner";

export const showSuccessToast = (msg: string) => toast.success(msg);
export const showErrorToast = (msg: string) => toast.error(msg);
export const showInfoToast = (msg: string) => toast.info(msg);
```

## Project Color Classes (Tailwind)
Use CSS variables for colors — already mapped in `tailwind.config.ts`:
```
bg-primary          → #004F39 (dark green)
text-primary        → #004F39
bg-background       → #FFFACA (cream yellow)
text-foreground     → #151613 (near black)
bg-secondary        → #D4EDE3 (soft light green)
text-muted-foreground → #3A3B2E
```
