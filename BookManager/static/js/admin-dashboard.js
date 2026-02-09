import { getCookie } from './utils.js';

export function initializeAdminFeaturedToggles() {
	const csrftoken = getCookie('csrftoken');
	const featuredButtons = document.querySelectorAll('.toggle-featured');
	
	featuredButtons.forEach(button => {
		button.addEventListener('click', function () {
			const bookId = this.dataset.bookId;
			const btn = this;

			fetch(`/toggle-featured/${bookId}/`, {
				method: 'POST',
				headers: {
					'X-CSRFToken': csrftoken,
					'Content-Type': 'application/json',
				},
			})
			.then(response => response.json())
			.then(data => {
				if (data.is_featured) {
					btn.classList.remove('btn-outline-secondary', 'btn-outline-warning');
					btn.classList.add('btn-warning');
					btn.innerHTML = '<i class="bi bi-star-fill"></i>';
				} else {
					btn.classList.remove('btn-warning');
					btn.classList.add('btn-outline-secondary');
					btn.innerHTML = '<i class="bi bi-star"></i>';
				}
			})
			.catch(error => {
				console.error('Error:', error);
			});
		});
	});
}

document.addEventListener('DOMContentLoaded', initializeAdminFeaturedToggles);
