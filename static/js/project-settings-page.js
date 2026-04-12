const permission_denied = 'You do not have the permission to access this section';
async function loadTaskSection(){

}
async function loadRolesSection(){
    try{
        if(!djangoContext.permissions.can_modify_tasks){
            alert(permission_denied);
    }
    }catch (err){
        alert(err);
    }
}
async function loadProjectStatsSection(){
    try{
        var area = document.getElementsByClassName('project-related-posts').item(0);
        area.innerHTML = '';
        let content =
                `<h1>Project data</h1><br>
                <label htmlFor="project-title">Project title</label><input id="project-title" name="project-title" type="text"/><br>
                <label htmlFor="project-description">Project description</label><input id="project-desctiption" name="project-description" type="text"/><br>
                <label for="is-private">Is project private(can be accessed via invite only and is hidden to the search engine)</label><input id="is-private" name="privacy" type="checkbox"/><br>
                <h1>Techstack requirements</h1>`;
                try{  const apiUrl = '/projects/settings/'+djangoContext.project.name+'/api-project-domains';
                  const domain_tags =
                    await fetch(apiUrl, {headers: { 'X-Requested-With': 'XMLHttpRequest' }
                  });
                if (domain_tags.ok){
                    const data = await domain_tags.json();
                    const tags = data.domains;
                    tags.forEach(tag => {
                                content += `<p style="display:inline-block;">${tag.domain}</p> 
                                <button type="button" onclick="addDomainToLocalStorage('${tag.domain}',false)">Delete</button><br>`;
                    });
                }
                else{
                    content += `Could not load or find the project requirements`;
                }
            }catch (err){
                content += err.message;
                }
            content += `<div class="new-domains">`;
            content += `<input type="text" id="domain-input" placeholder="Add new domain for the project"/>
                        <br><button onclick="addDomainToLocalStorage('idc',true)">Add domain to project</button>`
                        +`<h1>Project tags(domains)</h1>`;
            content+=`<div id="pending-domains">
                            <p>No domains queued to be added</p>
                      </div><br>
                      <div id="pending-removed-domains">
                          <p>No domains queued to be removed</p>
                      </div>
                      <button id="save-domains" onclick="addDomainsToDb()" style="display: none;">Save new domains</button>`;
            content +=  `</div>`;
            try{  const apiUrl = '/projects/settings/'+djangoContext.project.name+'/api-project-domains';
                  const domain_tags =
                    await fetch(apiUrl, {headers: { 'X-Requested-With': 'XMLHttpRequest' }
                  });
              if (domain_tags.ok){
                const data = await domain_tags.json();
                const tags = data.domains;
                tags.forEach(tag=>{
                    content += `<p>${tag.domain}</p> <button type="button" onclick="queueForRemoval('${tag.domain}')">Delete domain</button><br>`;
                });
              }
              else{
                content += `Could not load the project domain tags`;
              }
            }catch (err){
                content += err.message;
            }
            content += `<input type="text" placeholder="Add new domain to project"/><br><button>Add domains to project</button>`;
            area.innerHTML=content;
    } catch (err) {
        alert(err);
    }
}
function renderPendingDomains() {
    const container = document.getElementById('pending-domains');
    const removed = document.getElementById("pending-removed-domains");
    const saveBtn = document.getElementById('save-domains');

    let draft = JSON.parse(localStorage.getItem('newDomains') || '[]');
    if (draft.length > 0) {
        container.innerHTML = '';
        container.innerHTML += draft.map((name, index) => `
        <div class="pending-tag" style="background: #eee; display: inline-block; padding: 5px; margin: 2px;">
            ${name} <button onclick="removeDomainFromLocalStorage(${index},true)">x</button>
        </div>
    `).join('');
    }
    else{
        container.innerHTML = '<p>No domains queued to be added </p>';
    }

    let forRemoval = JSON.parse(localStorage.getItem('removedDomains') || '[]');
    if(forRemoval.length > 0){
        removed.innerHTML = forRemoval.map((name, index) => `
        <div class="pending-tag" style="background: #eee; display: inline-block; padding: 5px; margin: 2px;">
            ${name} <button onclick="removeDomainFromLocalStorage(${index},false)">x</button>
        </div>
    `).join('');
    }
    else{
        removed.innerHTML = '<p> No domains queued for removal</p>';
    }
    saveBtn.style.display = (draft.length > 0 || forRemoval.length > 0) ? 'block' : 'none';
}
function removeDomainFromLocalStorage(index,rmfromadd) {
    const listName = (rmfromadd) ? 'newDomains' : 'removedDomains';
    let draft = JSON.parse(localStorage.getItem(listName) || '[]');
    draft.splice(index, 1);
    localStorage.setItem('newDomains', JSON.stringify(draft));
    renderPendingDomains();
}
function addDomainToLocalStorage(domain_name,queueforadd){
    if(queueforadd){
        var domainInput = document.getElementById('domain-input');
        var text = domainInput.value.trim();

        let draft = JSON.parse(localStorage.getItem('newDomains') || '[]');
        if(!draft.includes(text)){
            draft.push(text);
            localStorage.setItem('newDomains',JSON.stringify(draft));
        }
        domainInput.value='';
    }
    else{
        let draft = JSON.parse(localStorage.getItem('removedDomains') || '[]');
        if(!draft.includes(domain_name)){
            draft.push(domain_name);
            localStorage.setItem('removedDomains',JSON.stringify(draft));
        }
    }
    renderPendingDomains();
}
function addRequirementToLocalStorage(domain_name){
    var domainInput = document.getElementById('domain-input');
    var text = domainInput.value.trim();

    let draft = JSON.parse(localStorage.getItem('newDomains') || '[]');
    if(!draft.includes(text)){
        draft.push(text);
        localStorage.setItem('newDomains',JSON.stringify(draft));
    }
    domainInput.value='';
    renderPendingDomains();
}
async function addDomainsToDb(){
    const newDomains = JSON.parse(localStorage.getItem('newDomains') || '[]');
    const removedDomains = JSON.parse(localStorage.getItem('removedDomains') || '[]');
    const projectName = window.djangoContext.project.name;

    try {
        if (newDomains.length > 0) {
            const desiredUrl = `/projects/settings/${window.djangoContext.project.name}/api-add-domains`;
            const addRes = await fetch(desiredUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ 'newDomains': newDomains })
            });
            if (addRes.ok) localStorage.removeItem('newDomains');
        }

        if (removedDomains.length > 0) {
            const desiredUrl = `/projects/settings/${window.djangoContext.project.name}/api-remove-domains`;
            const remRes = await fetch(desiredUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ 'removedDomains': removedDomains })
            });
            if (remRes.ok) localStorage.removeItem('removedDomains');
        }

        alert("Changes saved successfully!");
        loadProjectStatsSection();
    } catch (err) {
        console.error(err);
        alert("An error occurred while saving changes.");
    }
}
function queueForRemoval(domainName) {
    let removed = JSON.parse(localStorage.getItem('removedDomains') || '[]');
    if (!removed.includes(domainName)) {
        removed.push(domainName);
        localStorage.setItem('removedDomains', JSON.stringify(removed));
        alert(removed);
    }
    renderPendingDomains();
}