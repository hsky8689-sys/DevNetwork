function getCookie(name){
            let cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                const cookies = document.cookie.split(';');
                for (let i = 0; i < cookies.length; i++) {
                    const cookie = cookies[i].trim();
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
}
function loadPage(context){
    const role = context.role;
    alert(role + ' ' + JSON.stringify(context));
    const domains_div = document.getElementsByClassName("project-domains");

    // Exemplu utilizare:
    //document.querySelector('h1').textContent += ` (User: ${context.user_username}, Role: ${role})`;
}
async function goToMainProjectPage(project_name){
    const desiredUrl = `/projects/project-page/${project_name}/`;
    const bailoutUrl = location.href;
    try{
        const response = await fetch(desiredUrl,{
            headers : {'X-Requested-With': 'XMLHttpRequest'}
        });
         if (response.ok) {
            location.href = desiredUrl;
        } else {
            alert('Nu ai permisiunea sau pagina nu există.');
        }
    }catch (error){
        alert('Couldnt load project page');
        location.href = bailoutUrl;
    }
}
async function goToProjectMembersPage(project_name){
    const desiredUrl = `/projects/project-page/${project_name}/project-members/`;
    const bailoutUrl = location.href;
    try {
        const response = await fetch(desiredUrl, {
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        });
        if (response.ok) {
            location.href = desiredUrl;
        } else {
            alert('Nu ai permisiunea sau pagina nu există.');
        }
    } catch (error) {
        alert('Eroare de conexiune!');
        location.href = bailoutUrl;
    }
}
document.addEventListener('DOMContentLoaded', () => {
    if (window.pageContext) {
        loadPage(window.pageContext);
    } else {
        console.error('Context lipsă!');
    }
});