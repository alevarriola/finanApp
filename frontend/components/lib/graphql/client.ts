export interface GraphQLResponse<T> {
  data?: T;
  errors?: { message: string; extensions?: Record<string, unknown> }[];
}

export async function graphqlRequest<T>(
  query: string,
  variables?: Record<string, unknown>
): Promise<T> {
  const response = await fetch("/api/backend", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, variables }),
  });

  const json: GraphQLResponse<T> = await response.json();

  if (json.errors && json.errors.length > 0) {
    const err = json.errors[0];
    const statusCode = (err.extensions?.statusCode as number) ?? 500;
    const error = new Error(err.message) as Error & { statusCode: number };
    error.statusCode = statusCode;
    throw error;
  }

  if (!json.data) {
    throw new Error("No data returned from server");
  }

  return json.data;
}
