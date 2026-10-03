import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

// Research API response type
interface ResearchResponse {
  topic: string;
  report: string;
  feedback: string;
  search_results: string;
  scraped_content: string;
}

// Research activity messages
// These are UI-only for now because the backend
// currently returns only the final response.
const researchActivities = [
  {
    title: "Thinking",
    description: "Understanding your research question...",
  },
  {
    title: "Searching",
    description: "Finding recent and relevant sources...",
  },
  {
    title: "Checking sources",
    description: "Looking for reliable and trustworthy information...",
  },
  {
    title: "Reading",
    description: "Reading the most relevant webpages...",
  },
  {
    title: "Analyzing",
    description: "Extracting important facts and findings...",
  },
  {
    title: "Connecting",
    description: "Comparing information across sources...",
  },
  {
    title: "Writing",
    description: "Organizing the research into a clear report...",
  },
  {
    title: "Fact checking",
    description: "Checking claims and source consistency...",
  },
  {
    title: "Reviewing",
    description: "Critically reviewing the research...",
  },
  {
    title: "Finalizing",
    description: "Putting everything together...",
  },
];

function App() {
  // User research topic
  const [topic, setTopic] = useState("");

  // Final research response
  const [result, setResult] = useState<ResearchResponse | null>(null);

  // Loading state
  const [loading, setLoading] = useState(false);

  // Error message
  const [error, setError] = useState("");

  // Current research activity
  const [activityIndex, setActivityIndex] = useState(0);

  // RESEARCH ACTIVITY TIMER
  /*
   * The backend currently executes the complete pipeline
   * before returning the response.
   *
   * Therefore the frontend cannot know the exact agent
   * currently running.
   *
   * For now we show realistic research activities that
   * change automatically while the request is running.
   *
   * Only the current activity is displayed.
   *
   * Later this can be replaced with real SSE/WebSocket events.
   */
  useEffect(() => {
    // Do nothing when research is not running
    if (!loading) {
      return;
    }

    // Start from the first activity
    setActivityIndex(0);

    // Change activity every 5 seconds
    const interval = setInterval(() => {
      setActivityIndex((current) => {
        // Move to the next activity
        if (current < researchActivities.length - 1) {
          return current + 1;
        }

        // Stay on the last activity
        return current;
      });
    }, 5000);

    // Cleanup timer
    return () => clearInterval(interval);
  }, [loading]);

  // START RESEARCH
  const handleResearch = async () => {
    // Validate input
    if (!topic.trim()) {
      setError("Please enter a research topic.");
      return;
    }

    // Reset previous state
    setLoading(true);
    setError("");
    setResult(null);
    setActivityIndex(0);

    try {
      // Send research request to FastAPI backend
      const response = await fetch("/api/research", {
        method: "POST",

        headers: {
          "Content-Type": "application/json",
        },

        body: JSON.stringify({
          topic: topic.trim(),
        }),
      });

      // Check API response
      if (!response.ok) {
        const errorData = await response.json();

        throw new Error(
          errorData.detail || `Request failed with status ${response.status}`,
        );
      }

      // Convert response to JSON
      const data: ResearchResponse = await response.json();

      // Store final research result
      setResult(data);
    } catch (err) {
      // Handle API errors
      setError(err instanceof Error ? err.message : "Something went wrong.");
    } finally {
      // Stop loading state
      setLoading(false);
    }
  };

  // Current activity shown in the UI
  const currentActivity = researchActivities[activityIndex];

  return (
    <div className="min-h-screen bg-[#f8fafc]">
      {/* HEADER */}
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto max-w-5xl px-6 py-5">
          <div className="flex items-center gap-3">
            {/* Application logo */}
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-slate-900 text-sm font-bold text-white">
              R
            </div>

            {/* Application title */}
            <div>
              <h1 className="text-base font-semibold text-slate-900">
                Multi-Agent Researcher
              </h1>

              <p className="text-xs text-slate-500">
                AI-powered research assistant
              </p>
            </div>
          </div>
        </div>
      </header>

      {/* MAIN CONTENT */}
      <main className="mx-auto max-w-5xl px-6 py-12">
        {/* ======================================================
            HERO / SEARCH
        ====================================================== */}

        {!result && !loading && (
          <section className="mx-auto max-w-3xl pt-10 text-center">
            {/* Small badge */}
            <div className="mb-4 inline-flex rounded-full border border-slate-200 bg-white px-3 py-1 text-xs text-slate-500 shadow-sm">
              Multi-agent AI research
            </div>

            {/* Main heading */}
            <h2 className="text-4xl font-semibold tracking-tight text-slate-900">
              Research anything.
              <br />
              Get a clear answer.
            </h2>

            {/* Description */}
            <p className="mx-auto mt-4 max-w-xl text-sm leading-6 text-slate-500">
              Search the web, verify sources, analyze information, and generate
              a structured research report.
            </p>

            {/* Search input */}
            <div className="mt-8 rounded-2xl border border-slate-200 bg-white p-2 shadow-sm">
              <div className="flex items-center gap-2">
                <input
                  type="text"
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                  onKeyDown={(e) => {
                    // Start research when Enter is pressed
                    if (e.key === "Enter") {
                      handleResearch();
                    }
                  }}
                  placeholder="What would you like to research?"
                  className="min-w-0 flex-1 bg-transparent px-4 py-3 text-sm outline-none placeholder:text-slate-400"
                />

                {/* Research button */}
                <button
                  onClick={handleResearch}
                  disabled={loading}
                  className="rounded-xl bg-slate-900 px-5 py-3 text-sm font-medium text-white transition hover:bg-slate-700 disabled:opacity-50"
                >
                  Research
                </button>
              </div>
            </div>

            {/* Error message */}
            {error && <p className="mt-3 text-sm text-red-600">{error}</p>}
          </section>
        )}

        {/* RESEARCH PROGRESS */}
        {loading && (
          <section className="mx-auto max-w-2xl pt-20">
            <div className="px-4">
              {/* Current assistant activity */}
              <div className="flex items-start gap-3">
                {/* Animated research icon */}
                <div className="relative mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center">
                  {/* Ping animation */}
                  <div className="absolute h-8 w-8 animate-ping rounded-full bg-slate-200 opacity-40" />

                  {/* Main icon */}
                  <div className="relative flex h-7 w-7 items-center justify-center rounded-full bg-slate-900 text-xs text-white">
                    ✦
                  </div>
                </div>

                {/* Current activity */}
                <div className="min-w-0">
                  {/* Activity title */}
                  <div className="flex items-center gap-2">
                    <p
                      key={currentActivity.title}
                      className="animate-pulse text-sm font-medium text-slate-900"
                    >
                      {currentActivity.title}
                    </p>

                    {/* Thinking dots */}
                    <span className="flex items-center gap-0.5">
                      <span className="h-1 w-1 animate-bounce rounded-full bg-slate-400 [animation-delay:-0.3s]" />

                      <span className="h-1 w-1 animate-bounce rounded-full bg-slate-400 [animation-delay:-0.15s]" />

                      <span className="h-1 w-1 animate-bounce rounded-full bg-slate-400" />
                    </span>
                  </div>

                  {/* Activity description */}
                  <p className="mt-1 text-sm leading-6 text-slate-500">
                    {currentActivity.description}
                  </p>
                </div>
              </div>
            </div>
          </section>
        )}

        {/* RESULTS */}
        {result && !loading && (
          <div className="space-y-6">
            {/* RESULT HEADER */}
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs font-medium uppercase tracking-wider text-slate-400">
                  Research
                </p>

                <h2 className="mt-1 text-2xl font-semibold text-slate-900">
                  {result.topic || topic}
                </h2>
              </div>

              {/* Start another research */}
              <button
                onClick={() => {
                  setResult(null);
                  setTopic("");
                  setError("");
                  setActivityIndex(0);
                }}
                className="rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm text-slate-600 hover:bg-slate-50"
              >
                New research
              </button>
            </div>

            {/* RESEARCH REPORT */}
            <section className="rounded-2xl border border-slate-200 bg-white shadow-sm">
              {/* Report header */}
              <div className="border-b border-slate-100 px-7 py-5">
                <div className="flex items-center gap-3">
                  <h3 className="font-semibold text-slate-900">
                    Research Report
                  </h3>

                  {/* Completed badge */}
                  <span className="rounded-full bg-green-50 px-2.5 py-1 text-xs font-medium text-green-700">
                    Completed
                  </span>
                </div>
              </div>

              {/* Markdown report */}
              <article className="max-w-none px-7 py-7">
                <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                  components={{
                    // H1 styling
                    h1: ({ children }) => (
                      <h1 className="mb-5 mt-2 text-3xl font-bold tracking-tight text-slate-900">
                        {children}
                      </h1>
                    ),

                    // H2 styling
                    h2: ({ children }) => (
                      <h2 className="mb-4 mt-8 border-b border-slate-100 pb-2 text-xl font-semibold text-slate-900">
                        {children}
                      </h2>
                    ),

                    // H3 styling
                    h3: ({ children }) => (
                      <h3 className="mb-3 mt-6 text-lg font-semibold text-slate-900">
                        {children}
                      </h3>
                    ),

                    // Paragraph styling
                    p: ({ children }) => (
                      <p className="mb-4 text-sm leading-7 text-slate-600">
                        {children}
                      </p>
                    ),

                    // List styling
                    ul: ({ children }) => (
                      <ul className="mb-5 ml-5 list-disc space-y-1">
                        {children}
                      </ul>
                    ),

                    // Ordered list styling
                    ol: ({ children }) => (
                      <ol className="mb-5 ml-5 list-decimal space-y-1">
                        {children}
                      </ol>
                    ),

                    // List item styling
                    li: ({ children }) => (
                      <li className="text-sm leading-7 text-slate-600">
                        {children}
                      </li>
                    ),

                    // Link styling
                    a: ({ href, children }) => (
                      <a
                        href={href}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="font-medium text-blue-600 hover:underline"
                      >
                        {children}
                      </a>
                    ),

                    // Bold text styling
                    strong: ({ children }) => (
                      <strong className="font-semibold text-slate-900">
                        {children}
                      </strong>
                    ),
                  }}
                >
                  {result.report}
                </ReactMarkdown>
              </article>
            </section>

            {/* CRITIC REVIEW */}
            <section className="rounded-2xl border border-slate-200 bg-white shadow-sm">
              {/* Critic header */}
              <div className="border-b border-slate-100 px-7 py-5">
                <h3 className="font-semibold text-slate-900">Critic Review</h3>

                <p className="mt-1 text-xs text-slate-400">
                  Quality analysis of the generated report
                </p>
              </div>

              {/* Critic content */}
              <article className="px-7 py-6">
                <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                  components={{
                    // Critic H1 styling
                    h1: ({ children }) => (
                      <h1 className="mb-5 text-2xl font-bold text-slate-900">
                        {children}
                      </h1>
                    ),

                    // Critic H2 styling
                    h2: ({ children }) => (
                      <h2 className="mb-3 mt-6 text-lg font-semibold text-slate-900">
                        {children}
                      </h2>
                    ),

                    // Critic paragraph styling
                    p: ({ children }) => (
                      <p className="mb-3 text-sm leading-7 text-slate-600">
                        {children}
                      </p>
                    ),

                    // Critic list styling
                    ul: ({ children }) => (
                      <ul className="mb-4 ml-5 list-disc space-y-1">
                        {children}
                      </ul>
                    ),

                    // Critic list item styling
                    li: ({ children }) => (
                      <li className="text-sm leading-7 text-slate-600">
                        {children}
                      </li>
                    ),

                    // Critic bold text styling
                    strong: ({ children }) => (
                      <strong className="font-semibold text-slate-900">
                        {children}
                      </strong>
                    ),
                  }}
                >
                  {result.feedback}
                </ReactMarkdown>
              </article>
            </section>

            {/* ==================================================
                SOURCES
            ================================================== */}

            <section className="rounded-2xl border border-slate-200 bg-white shadow-sm">
              {/* Sources header */}
              <div className="border-b border-slate-100 px-7 py-5">
                <h3 className="font-semibold text-slate-900">Sources</h3>

                <p className="mt-1 text-xs text-slate-400">
                  Sources discovered during the research process
                </p>
              </div>

              {/* Source content */}
              <article className="px-7 py-6">
                <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                  components={{
                    // Source H1 styling
                    h1: ({ children }) => (
                      <h1 className="mb-5 text-2xl font-bold text-slate-900">
                        {children}
                      </h1>
                    ),

                    // Source H2 styling
                    h2: ({ children }) => (
                      <h2 className="mb-3 mt-6 text-lg font-semibold text-slate-900">
                        {children}
                      </h2>
                    ),

                    // Source H3 styling
                    h3: ({ children }) => (
                      <h3 className="mb-2 mt-5 text-base font-semibold text-slate-900">
                        {children}
                      </h3>
                    ),

                    // Source paragraph styling
                    p: ({ children }) => (
                      <p className="mb-3 text-sm leading-7 text-slate-600">
                        {children}
                      </p>
                    ),

                    // Source list styling
                    ul: ({ children }) => (
                      <ul className="mb-4 ml-5 list-disc space-y-1">
                        {children}
                      </ul>
                    ),

                    // Source list item styling
                    li: ({ children }) => (
                      <li className="text-sm leading-7 text-slate-600">
                        {children}
                      </li>
                    ),

                    // Source link styling
                    a: ({ href, children }) => (
                      <a
                        href={href}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="break-all font-medium text-blue-600 hover:underline"
                      >
                        {children}
                      </a>
                    ),

                    // Source bold text styling
                    strong: ({ children }) => (
                      <strong className="font-semibold text-slate-900">
                        {children}
                      </strong>
                    ),
                  }}
                >
                  {result.search_results}
                </ReactMarkdown>
              </article>
            </section>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
