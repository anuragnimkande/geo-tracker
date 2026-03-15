function showStatus(message, type) {
  const statusDiv = document.getElementById("status");
  const statusMessage = document.getElementById("statusMessage");

  // Check if elements exist
  if (!statusDiv || !statusMessage) return;

  const icon = statusDiv.querySelector(".fas");

  // Reset classes but preserve display
  const currentDisplay = statusDiv.style.display;
  statusDiv.className = "status";
  statusDiv.style.display = currentDisplay || "flex"; // Ensure it's visible

  // Set icon and class based on type
  if (type === "success") {
    if (icon) icon.className = "fas fa-check-circle";
    statusDiv.classList.add("success");
  } else if (type === "error") {
    if (icon) icon.className = "fas fa-exclamation-circle";
    statusDiv.classList.add("error");
  } else if (type === "info") {
    if (icon) icon.className = "fas fa-info-circle";
    statusDiv.classList.add("info");
  }

  statusMessage.textContent = message;

  // Clear any existing timeout
  if (window.statusTimeout) {
    clearTimeout(window.statusTimeout);
  }

  // Auto hide success messages after 4 seconds
  if (type === "success") {
    window.statusTimeout = setTimeout(() => {
      if (statusDiv.classList.contains("success")) {
        statusDiv.style.display = "none";
        statusDiv.classList.remove("success");
      }
    }, 4000);
  }
}

function setLoading(isLoading) {
  const alertBtn = document.getElementById("alertBtn");
  if (!alertBtn) return;

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
  const alertBtn = document.getElementById("alertBtn");
  if (!alertBtn || alertBtn.disabled) return;

  setLoading(true);

  if (!navigator.geolocation) {
    showStatus("Geolocation is not supported by your browser", "error");
    setLoading(false);
    return;
  }

  navigator.geolocation.getCurrentPosition(
    function (position) {
      const latitude = position.coords.latitude;
      const longitude = position.coords.longitude;
      const accuracy = position.coords.accuracy;

      console.log("Latitude:", latitude);
      console.log("Longitude:", longitude);
      console.log("Accuracy:", accuracy);

      showStatus(
        `📍 Location acquired (${Math.round(accuracy)}m precision). Sending alert...`,
        "info",
      );

      // Send to deployed server instead of localhost
      const apiURL = window.location.origin + "/send-location";

      fetch(apiURL, {
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
          console.error("Fetch error:", error);
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

      // FIXED: Use error codes correctly
      const errorMessages = {
        [1]: "Location access denied. Please enable location services.", // PERMISSION_DENIED
        [2]: "Location unavailable. Try moving to an open area.", // POSITION_UNAVAILABLE
        [3]: "Location request timed out. Please try again.", // TIMEOUT
      };

      showStatus(
        errorMessages[error.code] || "Unknown error occurred: " + error.message,
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
    e.target &&
    !e.target.matches("input, textarea")
  ) {
    e.preventDefault();
    sendLocation();
  }
});

// Add touch feedback with null check
if ("ontouchstart" in window) {
  const alertBtn = document.getElementById("alertBtn");
  if (alertBtn) {
    alertBtn.addEventListener("touchstart", function () {
      this.style.transform = "scale(0.97)";
    });

    alertBtn.addEventListener("touchend", function () {
      this.style.transform = "";
    });

    alertBtn.addEventListener("touchcancel", function () {
      this.style.transform = "";
    });
  }
}
