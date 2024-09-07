document.addEventListener("DOMContentLoaded", () => {
    const resultsTable = document.getElementById("resultsTable");
    const form = document.querySelector("form");
    const openCreateModalButton = document.getElementById("openCreateModal");
    const createCveModal = new bootstrap.Modal(document.getElementById("createCveModal"));
    const createCveForm = document.getElementById("createCveForm");

    async function searchAndRender(params = {}) {
        const cveRecordsData = await searchCVE(params);
        if (cveRecordsData) {
            renderResults(cveRecordsData.items, cveRecordsData.total, cveRecordsData.page, cveRecordsData.size, cveRecordsData.pages);
        }
    }

    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const query = document.getElementById("query").value || "";
        const startDate = document.getElementById("start_date").value || "";
        const endDate = document.getElementById("end_date").value || "";

        const params = {
            pk: query, start_date: startDate, end_date: endDate, page: 1, size: 10
        };

        await searchAndRender(params);
    });

    async function fetchCVEById(cveId) {
        try {
            const response = await fetch(`/api/v1/cve/${cveId}`);
            if (!response.ok) {
                throw new Error("CVE not found");
            }
            const data = await response.json();
            return data;
        } catch (error) {
            console.error("Error fetching CVE by ID:", error);
        }
    }

    async function searchCVE(params = {}) {
        // Додаємо параметри для пагінації
        const page = params.page || 1;
        const size = params.size || 10;

        const queryParams = new URLSearchParams({
            ...params, page: page, size: size
        });

        try {
            const response = await fetch(`/api/v1/cve/list?${queryParams.toString()}`);
            if (!response.ok) throw new Error("Failed to fetch data");
            return await response.json();
        } catch (error) {
            console.error("Error fetching CVE records:", error);
        }
    }


    async function createCVE(cveData) {
        try {
            const response = await fetch('/api/v1/cve/create', {
                method: 'POST', headers: {
                    'Content-Type': 'application/json',
                }, body: JSON.stringify(cveData),
            });
            if (!response.ok) {
                throw new Error("Error creating CVE");
            }
            const data = await response.json();
            return data;
        } catch (error) {
            console.error("Error creating CVE:", error);
        }
    }

    async function updateCVE(cveId, updateData) {
        try {
            const response = await fetch(`/api/v1/cve/${cveId}`, {
                method: 'PATCH', headers: {
                    'Content-Type': 'application/json',
                }, body: JSON.stringify(updateData),
            });
            if (!response.ok) {
                throw new Error("Error updating CVE");
            }
            const data = await response.json();
            return data;
        } catch (error) {
            console.error("Error updating CVE:", error);
        }
    }

    async function deleteCVE(cveId) {
        try {
            const response = await fetch(`/api/v1/cve/${cveId}`, {
                method: 'DELETE',
            });
            if (!response.ok) {
                throw new Error("Error deleting CVE");
            }
            console.log("CVE deleted successfully");
        } catch (error) {
            console.error("Error deleting CVE:", error);
        }
    }

    function renderResults(cveRecords, totalItems, currentPage, pageSize, totalPages) {
        const resultsTable = document.getElementById("resultsTable");
        if (!resultsTable) {
            console.error("Element with ID 'resultsTable' not found.");
            return;
        }

        resultsTable.innerHTML = `
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Assigner Org ID</th>
                    <th>State</th>
                    <th>Assigner Short Name</th>
                    <th>Date Published</th>
                    <th>Problem Types</th>
                </tr>
            </thead>
            <tbody>
                ${cveRecords.map(cve => `
                    <tr>
                        <td><a href="/details/${cve.id}"target="_blank">${cve.id}</a></td>
                        <td>${cve.assigner_org_id}</td>
                        <td>${cve.state}</td>
                        <td>${cve.assigner_short_name}</td>
                        <td>${new Date(cve.date_published).toLocaleDateString()}</td>
                        <td>
                            <ul>
                                ${cve.problem_types.map(pt => `<li>${pt.description}</li>`).join('')}
                            </ul>
                        </td>
                    </tr>
                `).join('')}
            </tbody>
        `;

        renderPaginationControls(currentPage, totalPages);
    }

    function renderPaginationControls(currentPage, totalPages) {
        const paginationControls = document.getElementById("paginationControls");
        if (!paginationControls) {
            console.error("Element with ID 'paginationControls' not found.");
            return;
        }

        let paginationHTML = `
        <li class="page-item ${currentPage === 1 ? 'disabled' : ''}">
            <a class="page-link" href="#" data-page="${currentPage - 1}">Previous</a>
        </li>
    `;

        const startPage = Math.max(1, currentPage - 1);
        const endPage = Math.min(totalPages, currentPage + 1);

        for (let i = startPage; i <= endPage; i++) {
            paginationHTML += `
            <li class="page-item ${i === currentPage ? 'active' : ''}">
                <a class="page-link" href="#" data-page="${i}">${i}</a>
            </li>
        `;
        }

        paginationHTML += `
        <li class="page-item ${currentPage === totalPages ? 'disabled' : ''}">
            <a class="page-link" href="#" data-page="${currentPage + 1}">Next</a>
        </li>
    `;

        paginationControls.innerHTML = paginationHTML;

        document.querySelectorAll(".page-link").forEach(button => {
            button.addEventListener("click", async (e) => {
                e.preventDefault();
                const page = parseInt(e.target.getAttribute("data-page"));
                if (page > 0 && page <= totalPages) {
                    const query = document.getElementById("query").value || "";
                    const startDate = document.getElementById("start_date").value || "";
                    const endDate = document.getElementById("end_date").value || "";

                    const params = {
                        pk: query, start_date: startDate, end_date: endDate, page: page, size: 10
                    };

                    await searchAndRender(params);
                }
            });
        });
    }
});

async function saveCVE() {
        const cveForm = document.getElementById("cveDetails");
        const formData = new FormData(cveForm);
        const cveData = Object.fromEntries(formData.entries());
        const cveId = cveData.id;

        try {
            const response = await fetch(`/api/v1/cve/${cveId}`, {
                method: 'PATCH', headers: {
                    'Content-Type': 'application/json',
                }, body: JSON.stringify(cveData),
            });
            if (!response.ok) {
                throw new Error("Error updating CVE");
            }
            alert("CVE updated successfully");
        } catch (error) {
            console.error("Error updating CVE:", error);
        }
    }

    async function deleteCVEFromForm() {
            const cveId = document.getElementById("cveId").value;
            if (confirm("Are you sure you want to delete this CVE?")) {
                try {
                    const response = await fetch(`/api/v1/cve/${cveId}`, {
                        method: 'DELETE',
                    });
                    if (!response.ok) {
                        throw new Error("Error deleting CVE");
                    }
                    alert("CVE deleted successfully");
                    window.location.href = "/";
                } catch (error) {
                    console.error("Error deleting CVE:", error);
                }
            }
        }

