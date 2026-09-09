import { Icon } from "./Icon";

export function Header() {
  return (
    <header className="site-header">
      <a className="brand" href="#top" aria-label="Medical Report Analyzer home">
        <span className="brand-mark"><Icon name="pulse" /></span>
        <span>
          <strong>Medical Report Analyzer</strong>
          <small>Intelligent clinical insights</small>
        </span>
      </a>

      <nav className="header-nav" aria-label="Primary navigation">
        <a href="#workspace">Workspace</a>
        <a href="#results">Results</a>
        <a href="#privacy">Privacy</a>
      </nav>

      <div className="header-status">
        <span className="status-dot" />
        <span>Analysis workspace</span>
      </div>
    </header>
  );
}
