const choices = {
  local: {label:'CLOSER TO HOME',title:'Helpful context. Under your control.',description:'Run your choice of open-source or open-weight model through Ollama or LM Studio on your local network. Apple’s on-device model is a separate option on supported devices.',footnote:'Open-source and open-weight are not interchangeable: available code, weights, and usage rights depend on each model’s license. Local network models run on your computer; setup is required.'},
  token: {label:'BRING YOUR OWN TOKEN',title:'Your provider. Your decision.',description:'Connect an HTTPS OpenAI-compatible endpoint with your own API token using the provider settings. This can include a paid service with a compatible API; compatibility and costs depend on the provider.',footnote:'Tokens are stored in the device Keychain. Approved context leaves your device when sent to a remote endpoint. The current app labels this configuration “Private Server”; there is no built-in subscription or automatic cloud fallback.'},
  none: {label:'NO MODEL REQUIRED',title:'A useful companion, all on its own.',description:'Keep appointments, visit questions, notes, documents, and reminders together. Prepare and export a visit brief without connecting an AI provider.',footnote:'AI is optional. AI-generated explanations and summaries require an available model; your everyday organization does not.'}
};
const tabs = [...document.querySelectorAll('[role="tab"]')];
function selectTab(tab) {
  const choice = choices[tab.dataset.mode];
  tabs.forEach(item => {item.setAttribute('aria-selected',String(item === tab));item.tabIndex = item === tab ? 0 : -1;});
  document.querySelector('#panel-ai').setAttribute('aria-labelledby',tab.id);
  for (const field of ['label','title','description','footnote']) document.querySelector(`#ai-${field}`).textContent = choice[field];
}
tabs.forEach((tab,index) => {
  tab.addEventListener('click',() => selectTab(tab));
  tab.addEventListener('keydown',event => {
    let next;
    if (event.key === 'ArrowRight' || event.key === 'ArrowDown') next = (index + 1) % tabs.length;
    if (event.key === 'ArrowLeft' || event.key === 'ArrowUp') next = (index - 1 + tabs.length) % tabs.length;
    if (event.key === 'Home') next = 0;
    if (event.key === 'End') next = tabs.length - 1;
    if (next !== undefined) {event.preventDefault();selectTab(tabs[next]);tabs[next].focus();}
  });
});
