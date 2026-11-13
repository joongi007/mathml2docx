/* Runs only inside an allow-scripts frame with no same-origin permission. */
(async () => {
  'use strict';
  const status = document.getElementById('diagram-status');
  const source = document.getElementById('diagram-source').textContent;
  const target = document.getElementById('diagram');
  try {
    if (window.origin !== 'null' || window.parent === window) {
      throw new Error('Diagram rendering requires an opaque sandbox frame');
    }
    if (source.length > 20000 || /%%\s*\{/.test(source) || source.trimStart().startsWith('---')) {
      throw new Error('Diagram configuration is disabled');
    }
    mermaid.initialize({
      startOnLoad: false,
      securityLevel: 'strict',
      htmlLabels: false,
      suppressErrorRendering: true,
      maxTextSize: 20000,
      maxEdges: 300,
      secure: ['secure', 'securityLevel', 'startOnLoad', 'htmlLabels', 'flowchart',
        'maxTextSize', 'maxEdges', 'dompurifyConfig', 'themeCSS', 'themeVariables'],
      flowchart: {htmlLabels: false},
      dompurifyConfig: {FORBID_TAGS: ['script', 'foreignObject', 'iframe', 'object', 'embed', 'image', 'a']},
      theme: 'neutral',
      fontFamily: 'system-ui, sans-serif'
    });
    const {svg} = await mermaid.render('mermaid-diagram', source);
    target.innerHTML = svg;
    // Do not bind Mermaid callbacks or click handlers.
    status.hidden = true;
  } catch (_) {
    target.replaceChildren();
    status.textContent = document.documentElement.lang === 'ko'
      ? '다이어그램을 표시할 수 없습니다. 문서의 원문을 확인하세요.'
      : 'The diagram could not render. Read its source in the document.';
  }
})();
