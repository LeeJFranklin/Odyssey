document.addEventListener('DOMContentLoaded', function () {
  const carousel = document.querySelector(".carousel");
  const items = Array.from(carousel.children); // Get all carousel items
  const itemWidth = items[0].offsetWidth + 20; // Item width plus margin
  let currentOffset = 0; // Keeps track of the current scroll position

// Duplicate items 10 times to make the carousel appear seamless
for (let i = 0; i < 10; i++) { // Outer loop runs 10 times
  items.forEach(item => {
    carousel.appendChild(item.cloneNode(true)); // Clone each item and add it to the end
  });
}

  // Set up the transition for smooth scrolling
  carousel.style.transition = "transform 4s linear"; // Smooth continuous scrolling

  // Function to move the carousel
  function moveCarousel() {
    currentOffset += 1; // Increment the offset for continuous scrolling

    // Apply the transform for smooth movement
    carousel.style.transform = `translateX(-${currentOffset}px)`;

    // Reset when all items have scrolled past
    if (currentOffset >= items.length * (itemWidth * items.length)) {
      currentOffset = 0; // Reset the offset to create a seamless loop
      carousel.style.transition = "reverse"; // Temporarily disable transition
      carousel.style.transform = `translateX(0)`; // Reset position to the start

      // Re-enable the transition after the reset
      setTimeout(() => {
        carousel.style.transition = "transform 4s linear";
      }, 10);
    }

    // Request the next animation frame
    requestAnimationFrame(moveCarousel);
  }

  // Start the carousel animation
  moveCarousel();
});

