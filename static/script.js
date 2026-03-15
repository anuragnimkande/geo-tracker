function showStatus(message, type) {
  const statusDiv = document.getElementById("status");
  const statusMessage = document.getElementById("statusMessage");
  const icon = statusDiv.querySelector(".fas");

  // Reset classes
  statusDiv.className = "status";

  // Set icon and class based on type
  if (type === "success") {
    icon.className = "fas fa-check-circle";
    statusDiv.classList.add("success");
  } else if (type === "error") {
    icon.className = "fas fa-exclamation-circle";
    statusDiv.classList.add("error");
  } else if (type === "info") {
    icon.className = "fas fa-info-circle";
    statusDiv.classList.add("info");
  }

  statusMessage.textContent = message;

  // Auto hide success messages after 4 seconds
  if (type === "success") {
    setTimeout(() => {
      if (statusDiv.classList.contains("success")) {
        statusDiv.style.display = "none";
        statusDiv.classList.remove("success");
      }
    }, 4000);
  }
}

function setLoading(isLoading) {
  const alertBtn = document.getElementById("alertBtn");

  if (isLoading) {
    alertBtn.classList.add("loading");
    alertBtn.disabled = true;
    showStatus("Acquiring precise location...", "info");
  } else {
    alertBtn.classList.remove("loading");
    alertBtn.disabled = false;
  }
}

function sendLocation() {
  // Prevent multiple clicks
  const alertBtn = document.getElementById("alertBtn");
  if (alertBtn.disabled) return;

  setLoading(true);

  // Check for geolocation support
  if (!navigator.geolocation) {
    showStatus("Geolocation is not supported by your browser", "error");
    setLoading(false);
    return;
  }

  // Get current position with high accuracy
  navigator.geolocation.getCurrentPosition(
    function (position) {
      const latitude = position.coords.latitude;
      const longitude = position.coords.longitude;
      const accuracy = position.coords.accuracy;

      showStatus(
        `📍 Location acquired (${Math.round(accuracy)}m precision). Sending alert...`,
        "info",
      );

      // Send to server
      fetch("http://127.0.0.1:5000/send-location", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          latitude: latitude,
          longitude: longitude,
          accuracy: accuracy,
        }),
      })
        .then(async (res) => {
          if (!res.ok) {
            const errorData = await res.json().catch(() => ({}));
            throw new Error(errorData.message || "Network response was not ok");
          }
          return res.json();
        })
        .then((data) => {
          if (data.status === "success") {
            showStatus("✅ Emergency alert sent successfully", "success");
          } else {
            showStatus(
              data.message || "Failed to send emergency alert",
              "error",
            );
          }
        })
        .catch((error) => {
          console.error("Error:", error);
          showStatus(
            error.message || "Connection error. Please try again.",
            "error",
          );
        })
        .finally(() => {
          setLoading(false);
        });
    },
    function (error) {
      setLoading(false);

      // Handle specific geolocation errors
      const errorMessages = {
        [error.PERMISSION_DENIED]:
          "Location access denied. Please enable location services.",
        [error.POSITION_UNAVAILABLE]:
          "Location unavailable. Try moving to an open area.",
        [error.TIMEOUT]: "Location request timed out. Please try again.",
      };

      showStatus(
        errorMessages[error.code] || "Unknown error occurred",
        "error",
      );
    },
    {
      enableHighAccuracy: true,
      timeout: 15000,
      maximumAge: 0,
    },
  );
}

// Add keyboard support
document.addEventListener("keydown", (e) => {
  // Send alert on Space or Enter when not typing in an input
  if (
    (e.key === " " || e.key === "Enter") &&
    !e.target.matches("input, textarea")
  ) {
    e.preventDefault();
    sendLocation();
  }
});

// Add touch feedback
if ("ontouchstart" in window) {
  document
    .getElementById("alertBtn")
    .addEventListener("touchstart", function () {
      this.style.transform = "scale(0.97)";
    });

  document.getElementById("alertBtn").addEventListener("touchend", function () {
    this.style.transform = "";
  });
}
