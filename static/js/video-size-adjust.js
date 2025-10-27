/**
 * Aligns the header video (#video-to-resize) based on the header text (#text-to-measure).
 * 1. Sets the video width to match the text width.
 * 2. Calculates the vertical position (top) to center the video behind the text,
 * applying a different adjustment factor on mobile screens.
 */
function alignVideoToTextMidpoint() {
  // Get the DOM elements
  const textElement = document.getElementById('text-to-measure');
  const videoElement = document.getElementById('video-to-resize');

  // Proceed only if both elements exist on the page
  if (textElement && videoElement) {
    // --- Part 1: Sync the width ---
    // Get the current rendered width of the text element
    const textWidth = textElement.offsetWidth;
    // Set the video's width to match the text
    videoElement.style.width = `${textWidth}px`;
    // Ensure the video scales proportionally by setting height to auto
    videoElement.style.height = 'auto';

    // --- Part 2: Calculate vertical position ---
    // Get the position and dimensions of the text element relative to the viewport
    const textRect = textElement.getBoundingClientRect();
    // Define the breakpoint for mobile adjustment (matches Bootstrap's < XL)
    const mobileBreakpoint = 1200; // Adjusted based on previous comments, check if 1210 was intended
    const isMobile = window.innerWidth <= mobileBreakpoint; 
    
    let finalTopPosition;

    if (isMobile) {
      // --- MOBILE LOGIC ---
      // This factor determines how much to shift the video *up* relative to the text height.
      // 0.4 means shift up by 40% of the text's height.
      // Adjust this value (e.g., 0.3, 0.5) to fine-tune the mobile vertical alignment.
      const mobileCorrectionFactor = 0.4; //

      // Calculate the Y-coordinate of the text's vertical midpoint relative to the document
      // (includes scroll offset)
      const textMidpointY = textRect.top + (textRect.height / 2) + window.scrollY;
            
      // Calculate the offset amount based on the text height and factor
      const correctionOffset = textRect.height * mobileCorrectionFactor;

      // Apply the correction: subtract the offset to move the video *up*
      // (Top position is relative to the document, lower value = higher up)
      finalTopPosition = textMidpointY - correctionOffset;

    } else {
      // --- DESKTOP LOGIC ---
      // Simply align the video's vertical center with the text's vertical center.
      // Calculate the Y-coordinate of the text's vertical midpoint relative to the document.
      const textMidpointY = textRect.top + (textRect.height / 2) + window.scrollY;
      finalTopPosition = textMidpointY; // No correction needed on desktop
    }
    
    // --- Part 3: Apply the final calculated position ---
    // Set the 'top' CSS property of the video element.
    // 'transform: translate(-50%, -50%)' in separador.css handles the actual centering.
    videoElement.style.top = `${finalTopPosition}px`;
  }
}

// --- Event Listeners ---
// Run the alignment function once the initial HTML is loaded
window.addEventListener('DOMContentLoaded', alignVideoToTextMidpoint);
// Rerun the alignment function whenever the browser window is resized
window.addEventListener('resize', alignVideoToTextMidpoint);