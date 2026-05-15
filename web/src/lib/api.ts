const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function request<T>(url: string, body: unknown): Promise<T> {
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const err = await res.text();
    throw new Error(err || `HTTP ${res.status}`);
  }
  return res.json();
}

// ---- RAG ----
export async function ragQuery(question: string, topK = 5, sessionId?: string) {
  return request<{ answer: string; sources: { text: string; source: string; score: number }[] }>(
    `${API_BASE}/api/v1/rag/query`,
    { question, top_k: topK, session_id: sessionId }
  );
}

// ---- CodeGen ----
export async function generateCode(requirement: string, language = "ArkTS", includeTests = false) {
  return request<{ code: string; files: { filename: string; content: string }[]; explanation: string }>(
    `${API_BASE}/api/v1/codegen/generate`,
    { requirement, language, include_tests: includeTests }
  );
}

// ---- Diagnose ----
export async function diagnoseError(errorMessage: string, codeContext = "") {
  return request<{ diagnosis: string; fix_suggestions: string[]; related_docs: unknown[] }>(
    `${API_BASE}/api/v1/diagnose/`,
    { error_message: errorMessage, code_context: codeContext }
  );
}

// ---- Migrate ----
export async function migrateCode(androidCode: string, sourceLanguage = "Kotlin") {
  return request<{ migrated_code: string; migration_notes: string[]; before_after: { before: string; after: string } }>(
    `${API_BASE}/api/v1/migrate/`,
    { android_code: androidCode, source_language: sourceLanguage }
  );
}

// ---- Publish ----
export async function publishArticle(title: string, content: string, tags: string[] = []) {
  return request<{ article_id: string; url: string; status: string }>(
    `${API_BASE}/api/v1/publish/`,
    { title, content, tags }
  );
}
