import { Icon } from "./Icon";

export function Disclaimer() {
  return (
    <aside className="disclaimer" id="privacy">
      <span className="disclaimer-icon"><Icon name="shield" /></span>
      <div><strong>Privacy & medical disclaimer</strong><p>This tool is intended for educational and research purposes only and is not a medical device or a substitute for professional medical advice. Avoid uploading sensitive patient information unless it is necessary and appropriately authorized.</p></div>
    </aside>
  );
}
