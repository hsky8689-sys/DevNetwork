const permission_denied = 'You do not have the permission to access this section';
async function loadProjectStatsSection(){
    try{
        var area = document.getElementsByClassName('project-related-posts').item(0);
        area.innerHTML = '';
        let content =
                `<h1>Project data</h1><br>
                <label htmlFor="project-title">Project title</label><input id="project-title" name="project-title" type="text"/><br>
                <label htmlFor="project-description">Project description</label><input id="project-desctiption" name="project-description" type="text"/><br>
                <label for="is-private">Is project private(can be accessed via invite only and is hidden to the search engine)</label><input id="is-private" name="privacy" type="checkbox"/><br>
                <h1>Project domains</h1>`;
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
                    content += `Could not load or find the project domains`;
                }
            }catch (err){
                content += err.message;
                }
                content += `<div class="new-domains">`;
            content += `<input type="text" id="domain-input" placeholder="Add new domain for the project"/>
                        <br><button onclick="addDomainToLocalStorage('idc',true)">Add domain to project</button>`;
            content+=`<div id="pending-domains">
                            <p>No domains queued to be added</p>
                      </div><br>
                      <div id="pending-removed-domains">
                          <p>No domains queued to be removed</p>
                      </div>
                      <button id="save-domains" onclick="addDomainsToDb()" style="display: none;">Save new domains</button>`;
            content +=  `</div>`;
            content += `<h1>Project techstack requirements</h1>`;
            try{
                const desiredUrl = `/projects/settings/${window.djangoContext.project.name}/api-get-project-requirements`;
                const response = await fetch(desiredUrl,
                {headers: { 'X-Requested-With': 'XMLHttpRequest'}
                });
                if(response.ok){
                    const data = await response.json();
                    const requirementsMap = data.requirements;
                    Object.entries(requirementsMap).forEach(([sectionName,reqList]) => {
                    content += `<h3>${sectionName}</h3><button onclick="addSectionToLocalStorage('${sectionName}',false)">Delete section</button>`;
                        if (Array.isArray(reqList)) {
                            reqList.forEach(req => {
                            content += `
        <p style="display:inline-block;">${req.skill}</p> 
        <button type="button" onclick="addRequirementToLocalStorage(['${sectionName}', '${req.skill}'], false)">
            Delete
        </button><br>`;
                            });
                            content += `<input type="text" id="${sectionName}-domain-input" placeholder="Add new requirement for ${sectionName}"/>
                            <br><button onclick="addRequirementToLocalStorage('${sectionName}',true)">Add requirement to ${sectionName}</button>`;
                        }
                else{
                    console.log(sectionName+' does not have a list associated with id');
                }
            });
                }else{
                    alert(`Server error ${response.status}`);
                }
                content+=`<div id="pending-requirements">
                            <p>No requirements queued to be added</p>
                      </div><br>
                      <div id="pending-removed-requirements">
                          <p>No requirements queued to be removed</p>
                      </div>
                      <button id="save-requirements" onclick="addRequirementsToDb()" style="display: none;">Save new requirements</button>`;
            }catch (err){
                alert(err);
            }
            content += `<input type="text" id="new-section-name"/>`;
            content += `<button onclick="addSectionToLocalStorage('',true)">Add new section</button>`;
            content += `<button onclick="addSectionsToDb()">Save section changes</button>`
            area.innerHTML = content;
    } catch (err) {
        alert(err);
    }
}
async function loadTaskAdministrationSection(){
    var area = document.getElementsByClassName('project-related-posts').item(0);
    area.innerHTML = '';
    let newHtml = '';
    try{
        const desiredUrl = `/projects/settings/${djangoContext.project.name}/api-get-project-tasks`;
        const response = await fetch(desiredUrl,
            {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    }
                    });
        if(response.ok){
            const data = await response.json();
            const tasks = data.tasks;
            if(tasks != null && tasks.length > 0){
                tasks.forEach(task=>{
                        newHtml += `<h2>${task.name}</h2><br>
                                    <h2>${task.description}</h2><br>
                                    <h2>${task.start_date}</h2><br>
                                    <h2>${task.end_date}</h2>
                                    <button onclick="queueTaskForDeletion('${task.name}')">Delete task</button>
                                    <br>`;
                });
            }
            else{
                newHtml += `<p>No tasks added to this project...</p><br>`;
            }
            newHtml += `<form id="new-task" method="POST" onsubmit="addTask()">
                                <label for="title">Task title</label><br>
                                <input type="text" id="title" placeholder="Enter a title for the new task"/><br>
                                <label for="description">Task description</label><br>
                                <textarea id="description" placeholder="Enter a description for the new task"></textarea><br>
                                <label for="start-date"></label>
                                <input type="date" id="start-date"/>
                                <label for="end-date"></label><br>
                                <input type="date" id="end-date"/><br>
                                <button>Add task</button>
                        </form>
                        <button onclick="removeTasks()">Remove tasks</button>`;
            newHtml += `<div id="pending-tasks" style="display: grid;gap=10px;margin: 10px;">
                             
                        </div>`;
        }
        area.innerHTML = newHtml;
    }catch (error){
        alert(error);
    }
}
async function removeTasks(){
    try{
        const desiredUrl = `/projects/settings/${window.djangoContext.project.name}/api-remove-tasks`;
        const removed = JSON.parse(localStorage.getItem('removedTasks') || '[]');
        const response = await fetch(desiredUrl,
            {
                    method: 'DELETE',
                    headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                    'X-Requested-With': 'XMLHttpRequest',
                    },
                    body:JSON.stringify({ 'removedTasks': removed })
                }
                );
        if(response.ok){
            localStorage.removeItem('removedTasks');
            await loadTaskAdministrationSection();
        }
        else{
            const errorData = await response.json();
            alert("Server error: " + (errorData.status || response.statusText));
        }
    }catch (error){
        alert(error);
    }
}
function queueTaskForDeletion(task){
     let removed = JSON.parse(localStorage.getItem('removedTasks') || '[]');
     if (!removed.includes(task)) {
        removed.push(task);
        localStorage.setItem('removedTasks', JSON.stringify(removed));
    }
    renderPendingTasks();
}
function renderPendingTasks(){
    var container = document.getElementById("pending-tasks");
    if(!container)return;
    let removed = JSON.parse(localStorage.getItem('removedTasks') || '[]');
    if (removed.length > 0) {
        container.innerHTML = removed.map((req, index) => `
            <div class="pending-tag" style="background: #e3f2fd; display: inline-block; padding: 5px; margin: 2px; border-radius:4px;">
                <strong>${req[0]}:</strong> ${req[1]} 
                <button onclick="removeTaskFromLocalStorage(${index})">x</button>
            </div>
        `).join('');
}
}
async function addTask(){
    event.preventDefault();
     const form = document.getElementById("new-task");
     const formData = new FormData(form);
     const data = {
        title: document.getElementById('title').value,
        description: document.getElementById('description').value,
        start_date: document.getElementById('start-date').value,
        end_date: document.getElementById('end-date').value,
     };
     try{
        const desiredUrl = `/projects/settings/${djangoContext.project.name}/api-add-task`;
        const response = await fetch(desiredUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(data)
        });
        if (response.ok) {
            const result = await response.json();
            form.reset();
            await loadTaskAdministrationSection();
        } else {
            alert("Eroare la server: " + response.status);
        }
     }catch (error){
        console.error("Error:",error);
     }
}
function renderPendingRequirements(){
   const container = document.getElementById("pending-requirements");
    const removed = document.getElementById("pending-removed-requirements");
    const saveBtn = document.getElementById("save-requirements");

    if (!container || !removed) return;

    let addedQueue = JSON.parse(localStorage.getItem('newRequirements') || '[]');
    if (addedQueue.length > 0) {
        container.innerHTML = addedQueue.map((req, index) => `
            <div class="pending-tag" style="background: #e3f2fd; display: inline-block; padding: 5px; margin: 2px; border-radius:4px;">
                <strong>${req[0]}:</strong> ${req[1]} 
                <button onclick="removeRequirementFromLocalStorage(${index}, true)">x</button>
            </div>
        `).join('');
    } else {
        container.innerHTML = '<p>No requirements queued to be added</p>';
    }

    let removedQueue = JSON.parse(localStorage.getItem('removedRequirements') || '[]');
    if (removedQueue.length > 0) {
        removed.innerHTML = removedQueue.map((name, index) => `
            <div class="pending-tag" style="background: #ffebee; display: inline-block; padding: 5px; margin: 2px; border-radius:4px;">
                ${name} <button onclick="removeRequirementFromLocalStorage(${index}, false)">x</button>
            </div>
        `).join('');
    } else {
        removed.innerHTML = `<p>No requirements queued to be removed</p>`;
    }

    saveBtn.style.display = (addedQueue.length > 0 || removedQueue.length > 0) ? 'block' : 'none';
}
function removeTaskFromLocalStorage(index){
    let draft = JSON.parse(localStorage.getItem('removedTasks') || '[]');
    draft.splice(index, 1);
    localStorage.setItem('removedTasks', JSON.stringify(draft));
    renderPendingRequirements();
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
    localStorage.setItem(listName, JSON.stringify(draft));
    renderPendingDomains();
}
function addSectionToLocalStorage(section_name,queueforadd){
    if(queueforadd){
        let draft = JSON.parse(localStorage.getItem('newSections') || '[]');
        const name = document.getElementById("new-section-name").value.trim();
        if(!draft.includes(name)){
            draft.push(name);
            localStorage.setItem('newSections',JSON.stringify(draft));
        }
    }
    else{
        let draft = JSON.parse(localStorage.getItem('removedSections') || '[]');
        if(!draft.includes(section_name)){
            draft.push(section_name);
            localStorage.setItem('removedSections',JSON.stringify(draft));
            /*hide the input to add different skills or delete them from that section TODO*/
        }
    }
}
async function addSectionsToDb(){
    const newSections = JSON.parse(localStorage.getItem('newSections') || '[]');
    const removedSections = JSON.parse(localStorage.getItem('removedSections') || '[]');
    if(newSections.length>0){
        try{
            const desiredUrl = `/projects/settings/${window.djangoContext.project.name}/api-add-requirement-sections`;
            const response = await fetch(desiredUrl,{
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ 'newSections': newSections })
            });
            if(response.ok){localStorage.removeItem('newSections');}
        }catch (err){
            alert(err);
        }
        loadProjectStatsSection();
    }
    if(removedSections.length>0){
        try{
            const desiredUrl = `/projects/settings/${window.djangoContext.project.name}/api-remove-requirement-sections`;
            const response = await fetch(desiredUrl,{
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ 'removedSections': removedSections })
            });
            if(response.ok){localStorage.removeItem('removedSections');}
        }catch (err){
            alert(err);
        }
    }
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
function addRequirementToLocalStorage(requested_name,queryforadd){
    if(queryforadd){
        var domainInput = document.getElementById(requested_name+'-domain-input');
        var text = domainInput.value.trim();

        let draft = JSON.parse(localStorage.getItem('newRequirements') || '[]');
        if(!draft.includes(text)){
            let newReq = [requested_name,text];
            draft.push(newReq);
            localStorage.setItem('newRequirements',JSON.stringify(draft));
        }
    domainInput.value='';
    }
    else{
        let draft = JSON.parse(localStorage.getItem('removedRequirements') || '[]');
        if(!draft.includes(requested_name)){
            draft.push(requested_name);
            localStorage.setItem('removedRequirements',JSON.stringify(draft));
        }
    }
    renderPendingRequirements();
}
async function addRequirementsToDb(){
    const newRequirements = JSON.parse(localStorage.getItem('newRequirements') || '[]');
    const removedRequirements = JSON.parse(localStorage.getItem('removedRequirements') || '[]');
    if(newRequirements.length > 0){
        try{
            const desiredUrl = `/projects/settings/${window.djangoContext.project.name}/api-add-requirements`;
             const response = await fetch(desiredUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ 'newRequirements': newRequirements })
            });
            if(response.ok){localStorage.removeItem('newRequirements');}
        }
        catch (err){
            alert(err);
        }
    }
    if(removedRequirements.length > 0){
        try{
            const desiredUrl = `/projects/settings/${window.djangoContext.project.name}/api-remove-requirements`;
             const response = await fetch(desiredUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ 'removedRequirements': removedRequirements })
            });
            if(response.ok){localStorage.removeItem('removedRequirements');}
        }
        catch (err){
            alert(err);
        }
    }
    alert("Changes saved successfully!");
    loadProjectStatsSection();
}
async function addDomainsToDb(){
    const newDomains = JSON.parse(localStorage.getItem('newDomains') || '[]');
    const removedDomains = JSON.parse(localStorage.getItem('removedDomains') || '[]');
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
        await loadProjectStatsSection();
    } catch (err) {
        console.error(err);
        alert("An error occurred while saving changes.");
    }
}
function removeRequirementFromLocalStorage(index, rmfromadd) {
    const listName = rmfromadd ? 'newRequirements' : 'removedRequirements';
    let draft = JSON.parse(localStorage.getItem(listName) || '[]');
    draft.splice(index, 1);
    localStorage.setItem(listName, JSON.stringify(draft));
    renderPendingRequirements();
}
//project role
async function loadRolesSection(){
    await getProjectRoles();
    var area = document.getElementsByClassName('project-related-posts').item(0);
    area.innerHTML = ``;
    var roles = ``;

    area.innerHTML = roles;
}
async function getProjectRoles(){
    try{
        const desiredUrl = ``;
        const response = await fetch(`/projects/settings/${window.djangoContext.project.name}/api-get-roles`,
            {headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                }});
        if(response.ok){
            const data = await response.json();
            alert(data.roles);
            localStorage.setItem('roles',JSON.stringify(data.roles));
        }
    }catch (error){
        alert(error);
    }
}