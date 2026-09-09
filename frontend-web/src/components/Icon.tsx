import type { SVGProps } from "react";

type IconName =
  | "arrow"
  | "check"
  | "clipboard"
  | "document"
  | "download"
  | "file"
  | "lock"
  | "medical"
  | "pulse"
  | "shield"
  | "spark"
  | "stethoscope"
  | "trash"
  | "upload"
  | "warning";

interface IconProps extends SVGProps<SVGSVGElement> {
  name: IconName;
}

export function Icon({ name, ...props }: IconProps) {
  const common = {
    fill: "none",
    stroke: "currentColor",
    strokeLinecap: "round" as const,
    strokeLinejoin: "round" as const,
    strokeWidth: 1.8,
  };

  const paths: Record<IconName, React.ReactNode> = {
    arrow: <path d="M5 12h14m-6-6 6 6-6 6" />,
    check: <path d="m5 12 4 4L19 6" />,
    clipboard: <path d="M9 5h6m-7 0a2 2 0 0 0-2 2v12h12V7a2 2 0 0 0-2-2M9 9h6m-6 4h6m-6 4h3" />,
    document: <path d="M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9Zm0 0v6h6" />,
    download: <path d="M12 3v12m0 0 4-4m-4 4-4-4M5 21h14" />,
    file: <path d="M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9Zm0 0v6h6" />,
    lock: <path d="M7 10V7a5 5 0 0 1 10 0v3m-12 0h14v10H5Zm7 4v2" />,
    medical: <path d="M12 21s-7-4.35-7-10a4 4 0 0 1 7-2.65A4 4 0 0 1 19 11c0 5.65-7 10-7 10Z" />,
    pulse: <path d="M3 12h4l2-6 4 12 2-6h6" />,
    shield: <path d="M12 21s8-3.5 8-10V5l-8-3-8 3v6c0 6.5 8 10 8 10Z" />,
    spark: <path d="m12 3-1.2 5.8L5 10l5.8 1.2L12 17l1.2-5.8L19 10l-5.8-1.2L12 3Zm6 13-.5 2.5L15 19l2.5.5L18 22l.5-2.5L21 19l-2.5-.5L18 16Z" />,
    stethoscope: <path d="M6 3v5a4 4 0 0 0 8 0V3m-8 0H4m2 0h2m6 0h-2m2 0h2m-4 5v4a5 5 0 0 0 10 0v-1m0 0a2 2 0 1 0 0 4 2 2 0 0 0 0-4Z" />,
    trash: <path d="M4 7h16m-10 4v6m4-6v6M9 7V4h6v3m-9 0 1 14h10l1-14" />,
    upload: <path d="M12 16V4m0 0L8 8m4-4 4 4M5 20h14" />,
    warning: <path d="m12 4 9 16H3L12 4Zm0 6v4m0 3h.01" />,
  };

  return (
    <svg aria-hidden="true" viewBox="0 0 24 24" {...common} {...props}>
      {paths[name]}
    </svg>
  );
}
