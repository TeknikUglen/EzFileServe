function copyToClipboard(link, filename, host) {
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(link).then(function() {
      showToast(`📋 Copied link for ${filename} from ${host}`);
    }).catch(function(err) {
      showToast('Failed to copy: ' + err);
    });
  } else {
    const textarea = document.createElement("textarea");
    textarea.value = link;
    document.body.appendChild(textarea);
    textarea.select();
    try {
      document.execCommand('copy');
      showToast(`📋 Copied link for ${filename} from ${host}`);
    } catch (err) {
      showToast('Failed to copy: ' + err);
    }
    document.body.removeChild(textarea);
  }
}


function showToast(message, type = "info") {
  const validTypes = ["success", "error", "warning", "info"];
  if (!validTypes.includes(type)) {
    type = "info";
  }

  const container = document.getElementById("toast-container");
  const toast = document.createElement("div");
  toast.className = `toast toast-${type}`;
  toast.innerText = message;
  container.appendChild(toast);

  // Delay before fade starts
  setTimeout(() => {
    toast.classList.add("fade-out");

    // Only remove toast after ALL transitions complete
    const removeAfterTransition = (e) => {
      if (e.propertyName === "opacity") {
        toast.remove();
      }
    };

    toast.addEventListener("transitionend", removeAfterTransition, { once: true });
  }, 2000);
}


document.addEventListener('DOMContentLoaded', function () {
  const triggers = document.querySelectorAll('.toast-trigger');
  triggers.forEach(el => {
    const msg = el.dataset.message;
    const type = el.dataset.type || 'info';
    if (msg) {
      showToast(msg, type);
    }
  });
});


document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('.js-btn-enable').forEach(el => {
    el.disabled = false;
  });
});
