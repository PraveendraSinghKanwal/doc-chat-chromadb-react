const API_BASE_URL = 'http://localhost:8000'; // Change this to your FastAPI backend URL

export const uploadDocument = async (file, userId) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('user_id', userId);

  try {
    const response = await fetch(`${API_BASE_URL}/upload/`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error uploading file:', error);
    throw error;
  }
};

export const deleteDocument = async (fileId, userId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/files/`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        file_id: fileId,
        user_id: userId
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error deleting document:', error);
    throw error;
  }
};

export const askQuestion = async (text, userId, fileId = null) => {
  try {
    const response = await fetch(`${API_BASE_URL}/ask/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        text,
        user_id: userId,
        file_id: fileId
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error asking question:', error);
    throw error;
  }
};

export const listUserFiles = async (userId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/files/${userId}`, {
      method: 'GET',
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching user files:', error);
    throw error;
  }
};

export const getFileContent = async (userId, fileId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/files/${userId}/${fileId}/content`, {
      method: 'GET',
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.blob();
  } catch (error) {
    console.error('Error fetching file content:', error);
    throw error;
  }
}; 