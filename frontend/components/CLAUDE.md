# Components - Guide for Claude Agents

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

Important transaction-related components currently in use:
- `transactions/TransactionFormModal.tsx` - manual transaction creation
- `transactions/AiTransactionPanel.tsx` - natural-language preview entry
- `transactions/AiTransactionConfirmModal.tsx` - editable confirmation before save
- `transactions/TransactionList.tsx` - grouped list rendering

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

Current implementation detail:
- the real client now throws a typed error with:
  - `statusCode`
  - optional `errorType`
- AI-related UI should branch on `errorType` instead of parsing raw strings

## Toast Helpers (`lib/toast.ts`)

```typescript
import { toast } from "sonner";

export const showSuccessToast = (msg: string) => toast.success(msg);
export const showErrorToast = (msg: string) => toast.error(msg);
export const showInfoToast = (msg: string) => toast.info(msg);
```

## AI UI Rules
- AI preview is not a generic chat timeline; it is a guided transaction-capture surface
- preview and confirmation components must stay bilingual via `aiChat.*` translation keys
- if AI fails, prefer contextual inline feedback inside the AI panel first
- final persistence must still go through the normal create mutation and React Query invalidation flow
- if you touch AI flow wiring, prefer editing `AiTransactionWorkspace.tsx` instead of duplicating state across pages
- `/chat` keeps a browser-session history only; do not turn it into DB-backed chat history by accident

## Project Color Classes (Tailwind)
Use CSS variables for colors - already mapped in `tailwind.config.ts`:
```
bg-primary          → #004F39 (dark green)
text-primary        → #004F39
bg-background       → #FFFACA (cream yellow)
text-foreground     → #151613 (near black)
bg-secondary        → #D4EDE3 (soft light green)
text-muted-foreground → #3A3B2E
```
