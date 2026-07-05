import type { SVGProps } from "react";

const Others = (props: SVGProps<SVGSVGElement>) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    width="24"
    height="24"
    {...props}
  >
    <path d="M12 3v1" />
    <path d="M12 20v1" />
    <path d="M3 12h1" />
    <path d="M20 12h1" />
    <path d="M18.36 5.64l-.7.7" />
    <path d="M6.34 17.66l-.7.7" />
    <path d="M5.64 5.64l.7.7" />
    <path d="M17.66 17.66l.7.7" />
    <circle cx="12" cy="12" r="4" />
  </svg>
);

export default Others;
