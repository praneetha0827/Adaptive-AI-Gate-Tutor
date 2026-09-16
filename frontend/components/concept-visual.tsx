type ConceptVisualProps = { content: string };

export default function ConceptVisual({ content }: ConceptVisualProps) {
  const text = content.toLowerCase();

  if (text.includes("recursion") || text.includes("recursive")) {
    return <figure className="concept-visual recursion-visual"><figcaption>Trace the calls</figcaption><div className="call-stack"><span>factorial(1) returns 1</span><span>factorial(2) returns 2</span><span>factorial(3) returns 6</span></div><p>Each call waits until the base case gives it a value to return.</p></figure>;
  }
  if (text.includes("stack") || text.includes("lifo")) {
    return <figure className="concept-visual stack-visual"><figcaption>Last in, first out</figcaption><div className="stack-blocks"><span>pop</span><span>item C</span><span>item B</span><span>item A</span></div><p>The newest item sits at the top, so it leaves first.</p></figure>;
  }
  if (text.includes("binary search tree") || text.includes("bst")) {
    return <figure className="concept-visual tree-visual"><figcaption>Binary search tree rule</figcaption><div className="tree-root">8</div><div className="tree-branches"><span>3<br /><small>smaller</small></span><span>12<br /><small>larger</small></span></div><p>Every value to the left is smaller; every value to the right is larger.</p></figure>;
  }
  if (text.includes("dynamic programming")) {
    return <figure className="concept-visual grid-visual"><figcaption>Reuse smaller answers</figcaption><div className="value-grid"><span>0</span><span>1</span><span>1</span><span>1</span><span>2</span><span>3</span><span>1</span><span>3</span><span>6</span></div><p>Store solved subproblems once, then build the larger solution from them.</p></figure>;
  }
  return null;
}
