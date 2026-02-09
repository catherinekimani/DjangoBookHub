document.addEventListener('DOMContentLoaded', function () {
	const avatarInput = document.querySelector('input[type="file"][name="avatar"]');
	const avatarPreview = document.getElementById('avatarPreview');

	if (avatarInput) {
		avatarInput.addEventListener('change', function (e) {
			const file = e.target.files[0];
			if (file) {
				const reader = new FileReader();
				reader.onload = function (e) {
					if (avatarPreview.tagName === 'IMG') {
						avatarPreview.src = e.target.result;
					} else {
						const img = document.createElement('img');
						img.src = e.target.result;
						img.alt = 'Avatar preview';
						img.className = 'rounded-circle border';
						img.style.width = '100px';
						img.style.height = '100px';
						img.style.objectFit = 'cover';
						img.id = 'avatarPreview';
						avatarPreview.parentNode.replaceChild(img, avatarPreview);
					}
				};
				reader.readAsDataURL(file);
			}
		});
	}
});
