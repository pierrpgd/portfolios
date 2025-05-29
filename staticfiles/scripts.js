// Variables globales
let currentDeleteType = null;
let currentDeleteId = null;
let selectedProfile = null;

// Fonction utilitaire pour récupérer le jeton CSRF
function getCsrfToken() {
    // Essayer de récupérer le token depuis les cookies
    const cookieValue = document.cookie
        .split('; ')
        .find(row => row.startsWith('csrftoken='))
        ?.split('=')[1];
        
    if (cookieValue) return cookieValue;
    
    // Sinon, chercher dans le DOM
    const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
    if (csrfInput) return csrfInput.value;
    
    console.error('CSRF token not found in cookies or DOM');
    return '';
}

// Fonction pour ajouter une nouvelle section À propos
function addProfileSection() {
    // Créer un élément row factice avec des attributs vides
    const dummyRow = document.createElement('div');
    dummyRow.setAttribute('data-identifiant', '');
    dummyRow.setAttribute('data-name', '');
    
    // Ouvrir la popup avec le contenu vide
    showPopup(dummyRow, 'profileModal', 'profileModalContent');
    
    // Rendre tous les champs éditables
    const modal = document.getElementById('profileModal');
    modal.querySelectorAll('.editable-content').forEach(el => {
        el.contentEditable = true;
        el.focus();
    });
}

// Fonction pour ajouter une nouvelle section À propos
function addSkillSection() {
    // Créer un élément row factice avec des attributs vides
    const dummyRow = document.createElement('div');
    dummyRow.setAttribute('data-category', '');
    dummyRow.setAttribute('data-name', '');
    dummyRow.setAttribute('data-level', '');
    
    // Ouvrir la popup avec le contenu vide
    showPopup(dummyRow, 'skillModal', 'skillModalContent');
    
    // Rendre tous les champs éditables
    const modal = document.getElementById('skillModal');
    modal.querySelectorAll('.editable-content').forEach(el => {
        el.contentEditable = true;
        el.focus();
    });
}

// Fonction pour ajouter une nouvelle section À propos
function addAboutSection() {
    // Créer un élément row factice avec des attributs vides
    const dummyRow = document.createElement('div');
    dummyRow.setAttribute('data-content', '');
    
    // Ouvrir la popup avec le contenu vide
    showPopup(dummyRow, 'aboutModal', 'aboutModalContent');
    
    // Rendre tous les champs éditables
    const modal = document.getElementById('aboutModal');
    modal.querySelectorAll('.editable-content').forEach(el => {
        el.contentEditable = true;
        el.focus();
    });
}

// Fonction pour ajouter une nouvelle section À propos
function addExperienceSection() {
    // Créer un élément row factice avec des attributs vides
    const dummyRow = document.createElement('div');
    dummyRow.setAttribute('data-dates', '');
    dummyRow.setAttribute('data-company', '');
    dummyRow.setAttribute('data-position', '');
    dummyRow.setAttribute('data-location', '');
    dummyRow.setAttribute('data-description', '');
    dummyRow.setAttribute('data-url', '');
    dummyRow.setAttribute('data-skills', '');
    
    // Ouvrir la popup avec le contenu vide
    showPopup(dummyRow, 'experienceModal', 'experienceModalContent');
    
    // Rendre tous les champs éditables
    const modal = document.getElementById('experienceModal');
    modal.querySelectorAll('.editable-content').forEach(el => {
        el.contentEditable = true;
        el.focus();
    });
}

// Fonction pour ajouter une nouvelle section À propos
function addProjectSection() {
    // Créer un élément row factice avec des attributs vides
    const dummyRow = document.createElement('div');
    dummyRow.setAttribute('data-title', '');
    dummyRow.setAttribute('data-description', '');
    dummyRow.setAttribute('data-image-url', '');
    dummyRow.setAttribute('data-url', '');
    dummyRow.setAttribute('data-skills', '');
    
    // Ouvrir la popup avec le contenu vide
    showPopup(dummyRow, 'projectModal', 'projectModalContent');
    
    // Rendre tous les champs éditables
    const modal = document.getElementById('projectModal');
    modal.querySelectorAll('.editable-content').forEach(el => {
        el.contentEditable = true;
        el.focus();
    });
}

// Fonction pour ajouter une compétence à un élément
function addSkillToItem(modalId) {
    fetch(`/load_data/?identifiant=${selectedProfile}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                document.querySelector('#profile-data').innerHTML = `
                    <div class="alert alert-danger">${data.error}</div>
                `;
                return Promise.reject(data.error);
            }
            
            // Créer une nouvelle ligne vide pour stocker les données
            const dummyRow = document.createElement('div');
            dummyRow.setAttribute('data-id', '');
            dummyRow.setAttribute('data-category', '');
            dummyRow.setAttribute('data-name', '');
    
            // Créer la modale
            const modal = document.createElement('div');
            modal.id = 'skillModal';
            modal.className = 'modal';

            const uniqueCategories = [...new Set(data.skills.map(skill => skill.category))];
            
            modal.innerHTML = `
                <div class="modal-dialog" role="document">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Ajouter une compétence</h5>
                            <button type="button" class="close" data-dismiss="modal" aria-label="Close" id="modalCloseButton">&times;</button>
                        </div>
                        <div class="modal-body">
                            <div class="editable-field">
                                <span class="modal-content-info-title">Catégorie : </span> 
                                <select class="form-select" data-field="category">
                                    <option value="">Sélectionnez une catégorie</option>
                                    ${uniqueCategories.map(category => `
                                        <option value="${category}">${category}</option>
                                    `).join('')}
                                </select>
                            </div>
                            <div class="editable-field">
                                <span class="modal-content-info-title">Intitulé : </span> 
                                <select class="form-select" data-field="name">
                                    <option value="">Sélectionnez d'abord une catégorie</option>
                                </select>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" id="modalCancelButton">Annuler</button>
                            <button type="button" class="btn btn-primary" id="skillModalValidateButton">Ajouter</button>
                        </div>
                    </div>
                </div>
            `;
            
            document.body.appendChild(modal);
            
            // Initialiser la modale proprement
            $(modal).modal('show');

            // Après avoir créé la modal
            const categorySelect = modal.querySelector('[data-field="category"]');
            const nameSelect = modal.querySelector('[data-field="name"]');
            
            // Stocker les compétences par catégorie
            const skillsByCategory = {};
            data.skills.forEach(skill => {
                if (!skillsByCategory[skill.category]) {
                    skillsByCategory[skill.category] = [];
                }
                skillsByCategory[skill.category].push(skill);
            });
            
            // Écouter les changements de catégorie
            categorySelect.addEventListener('change', function() {

                if (this.value === '') {
                    nameSelect.innerHTML = '<option value="">Sélectionnez d\'abord une catégorie</option>';
                    return;
                }
                else {
                    nameSelect.innerHTML = '<option value="">Sélectionnez une compétence</option>';

                    const selectedCategory = this.value;
                
                    if (selectedCategory && skillsByCategory[selectedCategory]) {
                        skillsByCategory[selectedCategory].forEach(skill => {
                            const option = document.createElement('option');
                            option.value = skill.name;
                            option.textContent = skill.name;
                            nameSelect.appendChild(option);
                        });
                    }
                }
            });
            
            // Déclencher immédiatement le changement si une catégorie est déjà sélectionnée
            if (categorySelect.value) {
                categorySelect.dispatchEvent(new Event('change'));
            }
    
            // Gérer la validation
            document.getElementById('skillModalValidateButton').addEventListener('click', async function() {
                const category = modal.querySelector('[data-field="category"]').value;
                const name = modal.querySelector('[data-field="name"]').value;

                if (!category || !name) {
                    alert('Veuillez remplir tous les champs');
                    return;
                }

                const result = await saveModalContent(modal);

                if (result.success) {
                    // Mettre à jour l'affichage des compétences
                    const skillsField = document.querySelector(`#${modalId} [data-field="skills"]`);
                    if (skillsField) {
                        skillsField.textContent = skillsField.textContent ? 
                            `${skillsField.textContent},${result.data.id}` : result.data.id;
                    }

                    updateSkillsDisplay(modalId);
                    removeModal(modal);
                }
            });

            // Ajouter l'événement de fermeture
            document.querySelector(`#modalCloseButton`).onclick = function() {
                removeModal(modal);
            };

            // Ajouter l'événement d'annulation
            document.querySelector(`#modalCancelButton`).onclick = function() {
                removeModal(modal);
            };
            
            // Fermer la popup en cliquant en dehors
            window.onclick = function(event) {
                if (event.target == modal) {
                    removeModal(modal);
                }
            };
        });
}

async function updateSkillsDisplay(modalId) {
    if (!selectedProfile) {
        return;
    }

    const skillsField = document.querySelector(`#${modalId} [data-field="skills"]`);
    if (!skillsField) {
        return;
    }

    let skillsData = null;
    // Récupérer tous les Skills en BDD
    await fetch(`/load_data/?identifiant=${selectedProfile}`)
        .then(response => response.json())
        .then(data => {
            skillsData = data.skills;
        })
        .catch(error => console.error("Erreur:", error))

    const skillsNameField = document.querySelector(`#${modalId} #skills-name`);

    if (skillsNameField) {
        const skills = skillsField.textContent.split(',');
        if (skills.length > 0) {
            skillsNameField.innerHTML = skills.map(skillId => {
                const skill = skillsData.find(s => s.id == skillId);
                return `<span class="skill-badge">${skill.name}<button class="deleteSkill" data-skill-id="${skill.id}">×</button></span>`;
            }).join('');
        }
    }
}

// Fonction pour afficher une popup générique
function showPopup(row, modalId, contentId) {

    document.body.style.overflowY = 'hidden';

    let profileIdentifiant = '';
    let profileName = '';
    let profileTitle = '';
    let skillCategory = '';
    let skillName = '';
    let skillLevel = 0;
    let aboutContent = '';
    let experienceDates = '';
    let experienceCompany = '';
    let experiencePosition = '';
    let experienceLocation = '';
    let experienceDescription = '';
    let experienceUrl = '';
    let experienceSkills = '';
    let projectTitle = '';
    let projectDescription = '';
    let projectImageUrl = '';
    let projectUrl = '';
    let projectSkills = '';

    if (modalId === 'profileModal') {
        profileIdentifiant = row.getAttribute('data-identifiant');
        profileName = row.getAttribute('data-name');
        profileTitle = row.getAttribute('data-title');
    } else if (modalId === 'skillModal') {
        skillCategory = row.getAttribute('data-category');
        skillName = row.getAttribute('data-name');
        skillLevel = parseInt(row.getAttribute('data-level')) || 0;
    } else if (modalId === 'aboutModal') {
        aboutContent = row.getAttribute('data-content');
    } else if (modalId === 'experienceModal') {
        experienceDates = row.getAttribute('data-dates');
        experienceCompany = row.getAttribute('data-company');
        experiencePosition = row.getAttribute('data-position');
        experienceLocation = row.getAttribute('data-location');
        experienceDescription = row.getAttribute('data-description');
        experienceUrl = row.getAttribute('data-url');
        experienceSkills = row.getAttribute('data-skills');
    } else if (modalId === 'projectModal') {
        projectTitle = row.getAttribute('data-title');
        projectDescription = row.getAttribute('data-description');
        projectImageUrl = row.getAttribute('data-image-url');
        projectUrl = row.getAttribute('data-url');
        projectSkills = row.getAttribute('data-skills');
    }

    const title = modalId === 'profileModal' ? 'Profil' : 
                    modalId === 'aboutModal' ? 'À propos' : 
                    modalId === 'experienceModal' ? 'Expérience' : 
                    modalId === 'projectModal' ? 'Projet' : 
                    modalId === 'skillModal' ? 'Compétence' : '';
    
    // Créer la popup si elle n'existe pas déjà
    let modal = document.getElementById(modalId);
    let backdrop = document.getElementById('modalBackdrop');

    if (!modal) {
        modal = document.createElement('div');
        modal.id = modalId;
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-header">
                <button class="close" id="modalCloseButton">&times;</button>
            </div>
            <div class="modal-content">
                <div class="modal-content-title">${title}</div>
                ${modalId === 'profileModal' ? `
                    <div class="modal-content-info">
                        <div class="editable-field">
                            <span class="modal-content-info-title">Identifiant : </span> <span contenteditable="true" class="editable-content" data-field="identifiant">${profileIdentifiant}</span>
                        </div>
                        <div class="editable-field">
                            <span class="modal-content-info-title">Nom : </span> <span contenteditable="true" class="editable-content" data-field="name">${profileName}</span>
                        </div>
                        <div class="editable-field">
                            <span class="modal-content-info-title">Titre : </span> <span contenteditable="true" class="editable-content" data-field="title">${profileTitle}</span>
                        </div>
                    </div>
                ` : modalId === 'skillModal' ? `
                    <div class="modal-content-info">
                        <div class="editable-field">
                            <span class="modal-content-info-title">Catégorie : </span> <span contenteditable="true" class="editable-content" data-field="category">${skillCategory}</span>
                        </div>
                        <div class="editable-field">
                            <span class="modal-content-info-title">Nom : </span> <span contenteditable="true" class="editable-content" data-field="name">${skillName}</span>
                        </div>
                        <div class="editable-field">
                            <span class="modal-content-info-title">Niveau : </span> 
                            <input type="range" class="form-range" data-field="level" min="0" max="10" step="1" value="${skillLevel}" oninput="this.nextElementSibling.value = this.value" style="width: 100%; height: 10px; background: #000; -webkit-appearance: none; border-radius: 5px;">
                            <output style="display: inline-block; margin-left: 10px; font-weight: bold;">${skillLevel}</output>
                        </div>
                    </div>
                ` : modalId === 'experienceModal' ? `
                    <div class="modal-content-info">
                        <div class="editable-field">
                            <span class="modal-content-info-title">Période : </span> <span contenteditable="true" class="editable-content" data-field="dates">${experienceDates}</span>
                        </div>
                        <div class="editable-field">
                            <span class="modal-content-info-title">Poste : </span> <span contenteditable="true" class="editable-content" data-field="position">${experiencePosition}</span>
                        </div>
                        <div class="editable-field">
                            <span class="modal-content-info-title">Entreprise : </span> <span contenteditable="true" class="editable-content" data-field="company">${experienceCompany}</span>
                        </div>
                        <div class="editable-field">
                            <span class="modal-content-info-title">Localisation : </span> <span contenteditable="true" class="editable-content" data-field="location">${experienceLocation}</span>
                        </div>
                        <div class="editable-field">
                            <span class="modal-content-info-title">URL : </span> <span contenteditable="true" class="editable-content" data-field="url">${experienceUrl}</span>
                        </div>
                        <div class="editable-field d-flex align-items-center">
                            <span class="modal-content-info-title">Compétences : </span>
                            <span data-field="skills" style="display: none">${experienceSkills}</span>
                            <div id="skills-name"></div>
                            <button id="experienceSkillsButton" class="btn btn-sm btn-outline-primary rounded-circle ms-2" style="width: 25px; height: 25px; padding: 0" onclick="addSkillToItem('${modalId}')">
                                <i class="fas fa-plus"></i>
                            </button>
                        </div>
                        <span class="modal-content-info-title">Description : </span>
                        <div contenteditable="true" class="editable-content" data-field="description">${experienceDescription}</div>
                    </div>
                ` : modalId === 'projectModal' ? `
                    <div class="modal-content-info">
                        <div class="editable-field">
                            <span class="modal-content-info-title">Titre : </span> <span contenteditable="true" class="editable-content" data-field="title">${projectTitle}</span>
                        </div>
                        <div class="editable-field">
                            <span class="modal-content-info-title">Image URL : </span> <span contenteditable="true" class="editable-content" data-field="image_url">${projectImageUrl}</span>
                        </div>
                        <div class="editable-field">
                            <span class="modal-content-info-title">URL : </span> <span contenteditable="true" class="editable-content" data-field="url">${projectUrl}</span>
                        </div>
                        <div class="editable-field d-flex align-items-center">
                            <span class="modal-content-info-title">Compétences : </span>
                            <span data-field="skills" style="display: none">${projectSkills}</span>
                            <div id="skills-name"></div>
                            <button id="projectSkillsButton" class="btn btn-sm btn-outline-primary rounded-circle ms-2" style="width: 25px; height: 25px; padding: 0" onclick="addSkillToItem('${modalId}')">
                                <i class="fas fa-plus"></i>
                            </button>
                        </div>
                        <span class="modal-content-info-title">Description : </span>
                        <div contenteditable="true" class="editable-content" data-field="description">${projectDescription}</div>
                    </div>
                ` : `<span class="modal-content-info-title">Contenu : </span>
                    <div contenteditable="true" class="editable-content" data-field="content">${aboutContent}</div>`}
            </div>
            <div class="w-100 text-end mb-3">
                <button id="${modalId}ValidateButton" type="button" class="btn btn-primary">
                    Enregistrer
                </button>
            </div>
        `;
        document.body.appendChild(modal);
    }

    if (modalId === 'experienceModal' || modalId === 'projectModal') {
        updateSkillsDisplay(modalId);
    }

    // Ajout de l'écouteur d'événement pour le bouton Enregistrer
    document.getElementById(`${modalId}ValidateButton`).addEventListener('click', async function() {
        const result = await saveModalContent(modal);

        if (result.success) {
            removeModal(modal);
            refreshData();
        }
    });
    
    if (!backdrop) {
        backdrop = document.createElement('div');
        backdrop.id = 'modalBackdrop';
        backdrop.className = 'modal-backdrop';
        document.body.appendChild(backdrop);
    }

    // Récupérer l'ID de la ligne cliquée
    if (row.dataset.hasOwnProperty('id')) {
        modal.dataset.rowId = row.dataset.id;
    }
    
    // Afficher la popup et le fond
    modal.style.display = 'block';
    backdrop.style.display = 'block';
    
    // Ajouter l'événement de fermeture
    document.querySelector(`#${modalId} button.close`).onclick = function() {
        modal.style.display = 'none';
        backdrop.style.display = 'none';
    };
    
    // Fermer la popup en cliquant en dehors
    window.onclick = function(event) {
        if (event.target == backdrop || event.target == modal) {
            modal.style.display = 'none';
            backdrop.style.display = 'none';
        }
    };

    // Réattacher les gestionnaires d'événements aux nouvelles lignes
    setTimeout(() => {
        document.querySelectorAll(`.${modalId.replace('Modal', '')}-row`).forEach(row => {
            row.addEventListener('dblclick', function() {
                showPopup(row, modalId, contentId);
            });
        });
    }, 100);
}

// Fonction pour supprimer une modal
function removeModal(modal) {
    if (!modal) return;
    
    // Cacher la modale d'abord pour un meilleur feedback visuel
    modal.style.display = 'none';

    const backdrop = document.getElementById('modalBackdrop');
    if (backdrop) {
        backdrop.remove();
    }

    modal.remove();

    const remainingModals = document.querySelectorAll('.modal[style*="display: block"], .modal:not([style*="display: none"])');
    if (remainingModals.length === 0) {
        document.body.style.overflowY = 'auto';
    }
}

// Enregistrement des données dans la base de données
async function saveModalContent(modal) {
    const modalId = modal.id;
    
    // Gestion des nouvelles sections
    const isNew = !modal.dataset.hasOwnProperty('rowId');
    const requestData = {
        modalId: modalId,
        isNew: isNew,
        data: {}
    };

    // Récupérer les champs éditables
    const fieldsWithDataField = modal.querySelectorAll('[data-field]');
    fieldsWithDataField.forEach(field => {
        if (field.dataset.field === 'skills') {
            requestData.data[field.dataset.field] = field.value ? 
            field.value.trim().split(',').map(skill => skill.trim()) :
            field.textContent.trim().split(',').map(skill => skill.trim());
        } else {
            requestData.data[field.dataset.field] = field.value ?
            field.value.trim() :
            field.textContent.trim();
        }
    });

    requestData.data.profile = selectedProfile;

    // Ajouter l'ID seulement pour les modifications
    if (!isNew) {
        requestData.data.id = modal.dataset.rowId;
    }

    const csrfToken = getCsrfToken();       
    try {
        const response = await fetch('/save_data/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
                'X-Debug-Request': 'true'  
            },
            credentials: 'include',  
            body: JSON.stringify(requestData)
        });
        
        let result;
        try {
            const responseText = await response.text();
            
            if (responseText) {
                result = JSON.parse(responseText);
            } else {
                console.error('[saveModalContent] La réponse est vide');
                throw new Error('La réponse du serveur est vide');
            }
        } catch (error) {
            console.error('[saveModalContent] Erreur lors de l\'analyse de la réponse:', error);
            alert('Erreur de format de la réponse du serveur. Voir la console pour plus de détails.');
            return;
        }
        
        // Vérifier si la réponse contient une erreur
        if (result && result.error) {
            const errorMsg = result.error.message || result.error;
            console.error('[saveModalContent] Erreur du serveur:', errorMsg);
            alert('Erreur: ' + errorMsg);
        }
        
        if (result.success) {
            if (result.type === 'profile') {
                selectedProfile = result.data.identifiant;
            }
        } else {
            console.error('[saveModalContent] Erreur du serveur:', result.error || 'Erreur inconnue');
        }

        return result;

    } catch (error) {
        console.error('[saveModalContent] Erreur lors de la sauvegarde:', error);
        return { error: error.message };
    }
}

// Rafraîchissement des données
async function refreshData() {
    try {
        const response = await fetch(`/load_data/?identifiant=${selectedProfile}`);
        const data = await response.json();
        
        if (data.error) {
            console.error('[refreshData] Erreur:', data.error);
            return;
        }
        
        updateProfileData(data);
    } catch (error) {
        console.error('[refreshData] Erreur:', error);
    }
}

// Insertion des données dans la page
function updateProfileData(data) {
    // Mise à jour des données du profil
    if (data.profile) {
        let profileTable = document.querySelector('#profile-table tbody');
        const options = {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: 'numeric',
            minute: '2-digit',
            hour12: true
        };

        // Si le tableau n'est pas trouvé, on le crée
        if (!profileTable) {
            profileTable = document.querySelector('#profile-table-container');

            profileTable.innerHTML = `
                <table id="profile-table" class="table table-hover">
                    <thead>
                        <tr>
                            <th>Identifiant</th>
                            <th>Nom</th>
                            <th>Titre</th>
                            <th>Créé le</th>
                            <th>Mis à jour le</th>
                            <th></th>
                        </tr>
                    </thead>
                    <tbody>
                    </tbody>
                </table>
            `;
        }

        profileTable = document.querySelector('#profile-table tbody');

        // Si le tableau est trouvé...
        if (profileTable) {

            // ...on supprime l'ancienne valeur
            profileLine = profileTable.querySelector(`tr[data-id="${data.profile.id}"]`);
            if (profileLine) {
                profileLine.remove();
            }

            // ...on ajoute une nouvelle ligne
            profileTable.innerHTML += `
                <tr class="profile-row" data-id="${data.profile.id}" data-identifiant="${data.profile.identifiant}" data-name="${data.profile.name}" data-title="${data.profile.title}" data-created="${data.profile.created_at}" data-updated="${data.profile.updated_at}">
                    <td>${data.profile.identifiant}</td>
                    <td>${data.profile.name}</td>
                    <td>${data.profile.title}</td>
                    <td>${new Date(data.profile.created_at).toLocaleString('en-US', options)}</td>
                    <td>${new Date(data.profile.updated_at).toLocaleString('en-US', options)}</td>
                    <td class="text-end">
                        <button class="btn btn-danger btn-sm delete-profile" data-id="${data.profile.id}">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                </tr>
            `;

            // Réattacher les événements
            document.querySelectorAll('.profile-row').forEach(row => {
                row.addEventListener('dblclick', function() {
                    showPopup(row, 'profileModal', 'profileModalContent');
                });
            });

            // Sélection/désélection d'une ligne au clic
            document.querySelectorAll('.table tbody tr').forEach(row => {
                row.addEventListener('click', function(e) {
                // Ne pas traiter si le clic provient d'un bouton de suppression
                    if (e.target.closest('.btn-danger, .delete-profile, .delete-about, .delete-experience, .delete-project')) {
                        return;
                    }

                    const profileIdentifiant = this.querySelector('td:first-child').textContent;

                    if (!handleProfileSelection(this, profileIdentifiant)) {
                        return;
                    }

                    // Charger les données du profil sélectionné
                    loadProfileData(profileIdentifiant);
                });
            });
        }
    }

    // Mise à jour de la section Compétences
    if (data.skills && data.skills.length > 0) {
        let skillTable = document.querySelector('#skill-table tbody');

        if (!skillTable) {
            skillTable = document.querySelector('#skill-table-container');

            skillTable.innerHTML = `
                <table id="skill-table" class="table table-striped">
                    <thead>
                        <tr>
                            <th>Catégorie</th>
                            <th>Nom</th>
                            <th>Niveau</th>
                            <th class="text-end"></th>
                        </tr>
                    </thead>
                    <tbody>
                    </tbody>
                </table>
            `;
        }

        skillTable = document.querySelector('#skill-table tbody');

        if (skillTable) {
            skillTable.innerHTML = data.skills.map(skill => `
                <tr class="skill-row" data-id="${skill.id}" data-content="${skill.category}" data-name="${skill.name}" data-level="${skill.level}">
                    <td>${skill.category}</td>
                    <td>${skill.name}</td>
                    <td>${skill.level}</td>
                    <td class="text-end">
                        <button class="btn btn-danger btn-sm delete-skill" data-id="${skill.id}">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                    <input type="hidden" class="skill-id" value="${skill.id}">
                </tr>
            `).join('');

            // Réattacher les événements
            document.querySelectorAll('.skill-row').forEach(row => {
                row.addEventListener('dblclick', function() {
                    showPopup(row, 'skillModal', 'skillModalContent');
                });
            });
        }
    }
    
    // Mise à jour de la section About
    if (data.about && data.about.length > 0) {
        let aboutTable = document.querySelector('#about-table tbody');

        if (!aboutTable) {
            aboutTable = document.querySelector('#about-table-container');

            aboutTable.innerHTML = `
                <table id="about-table" class="table table-striped">
                    <tbody>
                    </tbody>
                </table>
            `;
        }

        aboutTable = document.querySelector('#about-table tbody');

        if (aboutTable) {
            aboutTable.innerHTML = data.about.map(about => `
                <tr class="about-row" data-id="${about.id}" data-content="${about.content}">
                    <td>${about.content}</td>
                    <td class="text-end">
                        <button class="btn btn-danger btn-sm delete-about" data-id="${about.id}">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                    <input type="hidden" class="about-id" value="${about.id}">
                </tr>
            `).join('');

            // Réattacher les événements
            document.querySelectorAll('.about-row').forEach(row => {
                row.addEventListener('dblclick', function() {
                    showPopup(row, 'aboutModal', 'aboutModalContent');
                });
            });
        }
    }
    
    // Mise à jour de la section Experience
    if (data.experience && data.experience.length > 0) {
        let expTable = document.querySelector('#experience-table tbody');

        if (!expTable) {
            expTable = document.querySelector('#experience-table-container');

            expTable.innerHTML = `
                <table id="experience-table" class="table table-hover">
                    <thead>
                        <tr>
                            <th>Période</th>
                            <th>Poste</th>
                            <th>Entreprise</th>
                            <th>Localisation</th>
                            <th>Description</th>
                            <th>URL</th>
                            <th class="text-end"></th>
                        </tr>
                    </thead>
                    <tbody>
                    </tbody>
                </table>
            `;
        }

        expTable = document.querySelector('#experience-table tbody');

        if (expTable) {
            expTable.innerHTML = data.experience.map(exp => `
                <tr class="experience-row" data-id="${exp.id}" data-description="${exp.description}" data-dates="${exp.dates}" data-position="${exp.position}" data-company="${exp.company}" data-location="${exp.location}" data-url="${exp.url}" data-skills="${exp.skills}">
                    <td>${exp.dates}</td>
                    <td>${exp.position}</td>
                    <td>${exp.company}</td>
                    <td>${exp.location}</td>
                    <td>${exp.description}</td>
                    <td>${exp.url}</td>
                    <td class="text-end">
                        <button class="btn btn-danger btn-sm delete-experience" data-id="${exp.id}">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                    <input type="hidden" class="experience-id" value="${exp.id}">
                </tr>
            `).join('');

            // Réattacher les événements
            document.querySelectorAll('.experience-row').forEach(row => {
                row.addEventListener('dblclick', function() {
                    showPopup(row, 'experienceModal', 'experienceModalContent');
                });
            });
        }
    }
    
    // Mise à jour de la section Projects
    if (data.projects && data.projects.length > 0) {
        let projectsTable = document.querySelector('#projects-table tbody');

        if (!projectsTable) {
            projectsTable = document.querySelector('#projects-table-container');

            projectsTable.innerHTML = `
                <table id="projects-table" class="table table-striped">
                    <thead>
                        <tr>
                            <th>Titre</th>
                            <th>Description</th>
                            <th>Image URL</th>
                            <th>URL</th>
                            <th class="text-end"></th>
                        </tr>
                    </thead>
                    <tbody>
                    </tbody>
                </table>
            `;
        }

        projectsTable = document.querySelector('#projects-table tbody');

        if (projectsTable) {
            projectsTable.innerHTML = data.projects.map(project => `
                <tr class="project-row" data-id="${project.id}" 
                    data-title="${project.title}" data-content="${project.description}" data-image-url="${project.image_url}" data-url="${project.url}" data-skills="${project.skills}">
                    <td>${project.title}</td>
                    <td>${project.description}</td>
                    <td>${project.image_url}</td>
                    <td>${project.url}</td>
                    <td class="text-end">
                        <button class="btn btn-danger btn-sm delete-project" data-id="${project.id}">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                    <input type="hidden" class="project-id" value="${project.id}">
                </tr>
            `).join('');

            // Réattacher les événements
            document.querySelectorAll('.project-row').forEach(row => {
                row.addEventListener('dblclick', function() {
                    showPopup(row, 'projectModal', 'projectModalContent');
                });
            });
        }
    }
}

// Fonction pour charger les données d'un profil
function loadProfileData(profileIdentifiant) {
    return fetch(`/load_data/?identifiant=${profileIdentifiant}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                document.querySelector('#profile-data').innerHTML = `
                    <div class="alert alert-danger">${data.error}</div>
                `;
                return Promise.reject(data.error);
            }

            // Créer le HTML pour les données
            const html = `
                <div class="card mb-4">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <h2 class="mb-0">Compétences</h2>
                        <button id="addSkillSectionButton" class="btn btn-primary btn-sm" onclick="addSkillSection()">
                            <i class="fas fa-plus"></i> Ajouter une compétence
                        </button>
                    </div>
                    <div id="skill-table-container" class="card-body">
                        ${data.skills.length > 0 ? `
                            <table id="skill-table" class="table table-striped">
                                <thead>
                                    <tr>
                                        <th>Catégorie</th>
                                        <th>Nom</th>
                                        <th>Niveau</th>
                                        <th class="text-end"></th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${data.skills.map(skill => `
                                        <tr class="skill-row" data-id="${skill.id}" data-category="${skill.category}" data-name="${skill.name}" data-level="${skill.level}">
                                            <td>${skill.category}</td>
                                            <td>${skill.name}</td>
                                            <td>${skill.level}</td>
                                            <td class="text-end">
                                                <button class="btn btn-danger btn-sm delete-skill" data-id="${skill.id}">
                                                    <i class="fas fa-trash"></i>
                                                </button>
                                            </td>
                                            <input type="hidden" class="skill-id" value="${skill.id}">
                                        </tr>
                                    `).join('')}
                                </tbody>
                            </table>
                        ` : `
                            <p>Aucune compétence trouvée</p>
                        `}
                    </div>
                </div>

                <div class="card mb-4">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <h2 class="mb-0">À propos</h2>
                        <button id="addAboutSectionButton" class="btn btn-primary btn-sm" onclick="addAboutSection()">
                            <i class="fas fa-plus"></i> Ajouter une section
                        </button>
                    </div>
                    <div id="about-table-container" class="card-body">
                        ${data.about.length > 0 ? `
                            <table id="about-table" class="table table-striped">
                                <tbody>
                                    ${data.about.map(about => `
                                        <tr class="about-row" data-id="${about.id}" data-content="${about.content}">
                                            <td>${about.content}</td>
                                            <td class="text-end">
                                                <button class="btn btn-danger btn-sm delete-about" data-id="${about.id}">
                                                    <i class="fas fa-trash"></i>
                                                </button>
                                            </td>
                                            <input type="hidden" class="about-id" value="${about.id}">
                                        </tr>
                                    `).join('')}
                                </tbody>
                            </table>
                        ` : `
                            <p>Aucune section About trouvée</p>
                        `}
                    </div>
                </div>

                <div class="card mb-4">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <h2>Expériences</h2>
                        <button id="addExperienceSectionButton" class="btn btn-primary btn-sm" onclick="addExperienceSection()">
                            <i class="fas fa-plus"></i> Ajouter une expérience
                        </button>
                    </div>
                    <div id="experience-table-container" class="card-body">
                        ${data.experience.length > 0 ? `
                            <table id="experience-table" class="table table-striped">
                                <thead>
                                    <tr>
                                        <th>Période</th>
                                        <th>Poste</th>
                                        <th>Entreprise</th>
                                        <th>Localisation</th>
                                        <th>Description</th>
                                        <th>URL</th>
                                        <th class="text-end"></th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${data.experience.map(exp => `
                                        <tr class="experience-row" data-id="${exp.id}" data-description="${exp.description}" data-dates="${exp.dates}" data-position="${exp.position}" data-company="${exp.company}" data-location="${exp.location}" data-url="${exp.url}" data-skills="${exp.skills}">
                                            <td>${exp.dates}</td>
                                            <td>${exp.position}</td>
                                            <td>${exp.company}</td>
                                            <td>${exp.location}</td>
                                            <td>${exp.description}</td>
                                            <td>${exp.url}</td>
                                            <td class="text-end">
                                                <button class="btn btn-danger btn-sm delete-experience" data-id="${exp.id}">
                                                    <i class="fas fa-trash"></i>
                                                </button>
                                            </td>
                                            <input type="hidden" class="experience-id" value="${exp.id}">
                                        </tr>
                                    `).join('')}
                                </tbody>
                            </table>
                        ` : `
                            <p>Aucune expérience trouvée</p>
                        `}
                    </div>
                </div>

                <div class="card mb-4">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <h2>Projets</h2>
                        <button id="addProjectSectionButton" class="btn btn-primary btn-sm" onclick="addProjectSection()">
                            <i class="fas fa-plus"></i> Ajouter un projet
                        </button>
                    </div>
                    <div id="projects-table-container" class="card-body">
                        ${data.projects.length > 0 ? `
                            <table id="projects-table" class="table table-striped">
                                <thead>
                                    <tr>
                                        <th>Titre</th>
                                        <th>Description</th>
                                        <th>Image URL</th>
                                        <th>URL</th>
                                        <th class="text-end"></th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${data.projects.map(project => `
                                        <tr class="project-row" data-id="${project.id}" data-title="${project.title}" data-description="${project.description}" data-image-url="${project.image_url}" data-url="${project.url}" data-skills="${project.skills}">
                                            <td>${project.title}</td>
                                            <td>${project.description}</td>
                                            <td>${project.image_url}</td>
                                            <td>${project.url}</td>
                                            <td class="text-end">
                                                <button class="btn btn-danger btn-sm delete-project" data-id="${project.id}">
                                                    <i class="fas fa-trash"></i>
                                                </button>
                                            </td>
                                            <input type="hidden" class="project-id" value="${project.id}">
                                        </tr>
                                    `).join('')}
                                </tbody>
                            </table>
                        ` : `
                            <p>Aucun projet trouvé</p>
                        `}
                    </div>
                </div>
            `;

            // Mettre à jour le DOM
            document.querySelector('#profile-data').innerHTML = html;

            // Ajouter les gestionnaires d'événements pour les lignes Compétences
            document.querySelectorAll('.skill-row').forEach(row => {
                row.addEventListener('dblclick', function() {
                    showPopup(row, 'skillModal', 'skillModalContent');
                });
            });
            
            // Ajouter les gestionnaires d'événements pour les lignes About
            document.querySelectorAll('.about-row').forEach(row => {
                row.addEventListener('dblclick', function() {
                    showPopup(row, 'aboutModal', 'aboutModalContent');
                });
            });

            // Ajouter les gestionnaires d'événements pour les lignes Experience
            document.querySelectorAll('.experience-row').forEach(row => {
                row.addEventListener('dblclick', function() {
                    showPopup(row, 'experienceModal', 'experienceModalContent');
                });
            });

            // Ajouter les gestionnaires d'événements pour les lignes Projects
            document.querySelectorAll('.project-row').forEach(row => {
                row.addEventListener('dblclick', function() {
                    showPopup(row, 'projectModal', 'projectModalContent');
                });
            });

            return data;
        })
        .catch(error => {
            console.error('Erreur:', error);
            document.querySelector('#profile-data').innerHTML = `
                <div class="alert alert-danger">Erreur lors du chargement des données</div>
            `;
            return Promise.reject(error);
        });
}

// Gestion de la sélection/déselection d'un profil
function handleProfileSelection(row, profileIdentifiant) {
    // Si c'est le même profil qui est cliqué, on désélectionne
    if (selectedProfile === profileIdentifiant) {
        // Désélectionner la ligne
        row.classList.remove('table-active');
        // Effacer les données affichées
        document.querySelector('#profile-data').innerHTML = `
            <div class="text-muted text-center py-5">
                Sélectionnez un profil pour voir ses données
            </div>`;
        selectedProfile = null;
        return false;
    }

    // Désélectionner toutes les lignes
    document.querySelectorAll('.table tbody tr').forEach(r => {
        r.classList.remove('table-active');
    });
    // Sélectionner la ligne cliquée
    row.classList.add('table-active');
    
    // Mettre à jour le profil sélectionné
    selectedProfile = profileIdentifiant;
    return true;
}

$(function() {

    // Gestion des clics sur les lignes de profils
    document.querySelectorAll('.profile-row').forEach(row => {
        // Double clic pour ouvrir la popup
        row.addEventListener('dblclick', function() {
            showPopup(row, 'profileModal', 'profileModalContent');
        });

        // Simple clic pour sélectionner le profil
        row.addEventListener('click', function(e) {
            // Ne pas traiter si le clic provient d'un bouton de suppression
            if (e.target.closest('.btn-danger, .delete-profile, .delete-about, .delete-experience, .delete-project, .delete-skill')) {
                return;
            }

            const profileIdentifiant = this.querySelector('td:first-child').textContent;

            // Gestion de la sélection/déselection d'un profil
            if (!handleProfileSelection(this, profileIdentifiant)) {
                return;
            }

            // Charger les données du profil sélectionné
            loadProfileData(profileIdentifiant);
        });
    });

    // Gestion des modales
    document.body.addEventListener('click', function(e) {

        const backdrop = document.getElementById('modalBackdrop');
        const modal = document.querySelector('.modal');

        // Clic sur le bouton de fermeture
        if (e.target && e.target.classList.contains('close')) {
            const modal = e.target.closest('.modal');
            if (modal) {
                modal.style.display = 'none';
                removeModal(modal);
            }
        }

        // Clic sur le backdrop
        if (backdrop && e.target === backdrop) {
            modal.style.display = 'none';
            removeModal(modal);
        }

    });

    // Confirmation de suppression d'un element
    $('#confirmDeleteButton').click(function() {
        const csrfToken = getCsrfToken();
        let url = `/delete_${currentDeleteType}/`
        if (currentDeleteType === 'skill') {
            url += `${selectedProfile}/${currentDeleteId}/`;
        } else {
            url += `${currentDeleteId}/`;
        }
        
        fetch(url, {
            method: 'DELETE',
            headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/json',
            },
            credentials: 'same-origin'
        })
        .then(response => {
            if (!response.ok) throw new Error('Network response was not ok');
            return response.json();
        })
        .then(data => {
            if (data.success) {
            $(`[data-id="${currentDeleteId}"]`).closest(`tr.${currentDeleteType}-row`).remove();
            if (currentDeleteType === 'profile') {
                // Effacer les données affichées
                document.querySelector('#profile-data').innerHTML = `
                    <div class="text-muted text-center py-5">
                        Sélectionnez un profil pour voir ses données
                    </div>`;
                selectedProfile = null;
                // Suppression du tableau des profils s'il est vide
                if (document.querySelectorAll('.profile-row').length === 0) {
                    document.querySelector('#profile-table-container').innerHTML = `
                        <p class="text-muted">Aucun profil trouvé</p>`;
                }
            }
            } else {
            alert('Erreur lors de la suppression: ' + (data.error || 'Erreur inconnue'));
            }
            $('#confirmDeleteModal').modal('hide');
        })
        .catch(error => {
            console.error('Error:', error);
            $('#confirmDeleteModal').modal('hide');
        });
    });

    // Clic sur le bouton de suppression
    $(document).on('click', '.delete-profile, .delete-about, .delete-experience, .delete-project, .delete-skill', function() {
        const btn = $(this);
        currentDeleteId = btn.data('id');
        
        if (btn.hasClass('delete-profile')) {
            currentDeleteType = 'profile';
        } else if (btn.hasClass('delete-about')) {
            currentDeleteType = 'about';
        } else if (btn.hasClass('delete-experience')) {
            currentDeleteType = 'experience';
        } else if (btn.hasClass('delete-project')) {
            currentDeleteType = 'project';
        } else {
            currentDeleteType = 'skill';
        }
        
        $('#confirmDeleteModal').modal('show');
    });

    $('#cancelDeleteButton').click(function() {
        $('#confirmDeleteModal').modal('hide');
    });

    // Ajout du gestionnaire d'événement pour la suppression
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('deleteSkill')) {
            const skillId = e.target.getAttribute('data-skill-id');
            
            // Suppression de l'ID de la competence
            const skills = document.querySelector('[data-field="skills"]');
            if (skills) {
                // Nettoyer les IDs vides et espaces
                const skillIds = skills.textContent.split(',')
                    .map(id => id.trim())
                    .filter(id => id !== '');
                
                const index = skillIds.indexOf(skillId);
                if (index > -1) {
                    skillIds.splice(index, 1);
                    skills.textContent = skillIds.join(',');
                }
            }

            // Suppression du nom de la competence
            e.target.parentElement.remove();
        }
    });
});