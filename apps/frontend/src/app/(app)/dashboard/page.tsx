export default function Dashboard() {
  return (
    <div className="flex flex-col flex-1 items-center justify-center bg-zinc-50 font-sans dark:bg-black">
      <main className="flex flex-1 w-full max-w-lg flex-col items-center justify-center gap-8 py-32 px-8">
        <h1 className="text-4xl font-bold tracking-tight text-slate-900 dark:text-zinc-50">
          Dashboard
        </h1>
        <p className="text-center text-lg text-zinc-600 dark:text-zinc-400">
          Welcome to the dashboard. You are logged in.
        </p>
      </main>
    </div>
  );
}
