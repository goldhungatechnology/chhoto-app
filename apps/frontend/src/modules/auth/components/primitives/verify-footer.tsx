export default function VerifyFooter() {
  return (
    <footer className="px-4 text-center">
      <p className="text-xs text-slate-500 dark:text-gray-400">
        Having trouble? Contact{" "}
        <a
          href="mailto:support@example.com"
          className="text-slate-700 hover:text-slate-900 underline transition-colors dark:text-primary"
        >
          support@chhoto.tech
        </a>
      </p>
    </footer>
  );
}
