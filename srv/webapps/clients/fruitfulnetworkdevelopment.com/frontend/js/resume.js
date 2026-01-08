function downloadResume() {
    // Create a temporary link element
    const link = document.createElement('a');
    
    // Set the path to your file
    link.href = '/assets/docs/resume.pdf';
    
    // The 'download' attribute forces the browser to download 
    // rather than open. You can also specify a filename here.
    link.download = 'resume.pdf';
    
    // Append to body, click, and remove
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }
