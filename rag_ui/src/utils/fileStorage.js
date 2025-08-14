const DB_NAME = 'DocumentStorage';
const STORE_NAME = 'documents';
const DB_VERSION = 1;

let db = null;

const initDB = () => {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, DB_VERSION);

    request.onerror = () => {
      reject('Error opening database');
    };

    request.onsuccess = (event) => {
      db = event.target.result;
      resolve(db);
    };

    request.onupgradeneeded = (event) => {
      const db = event.target.result;
      if (!db.objectStoreNames.contains(STORE_NAME)) {
        db.createObjectStore(STORE_NAME, { keyPath: 'id' });
      }
    };
  });
};

export const saveFile = async (file) => {
  if (!db) await initDB();

  // First, read the file
  const fileContent = await new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result);
    reader.onerror = () => reject(reader.error);
    reader.readAsDataURL(file);
  });

  // Then, create the transaction and save the file data
  return new Promise((resolve, reject) => {
    const transaction = db.transaction([STORE_NAME], 'readwrite');
    const store = transaction.objectStore(STORE_NAME);
    
    const fileData = {
      id: Date.now().toString(),
      name: file.name,
      type: file.type,
      size: file.size,
      content: fileContent,
      timestamp: new Date().toISOString()
    };

    const request = store.add(fileData);
    
    request.onsuccess = () => resolve(fileData);
    request.onerror = () => reject('Error saving file');
  });
};

export const getAllFiles = async () => {
  if (!db) await initDB();

  return new Promise((resolve, reject) => {
    const transaction = db.transaction([STORE_NAME], 'readonly');
    const store = transaction.objectStore(STORE_NAME);
    const request = store.getAll();

    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject('Error getting files');
  });
};

export const deleteFile = async (fileId) => {
  if (!db) await initDB();

  return new Promise((resolve, reject) => {
    const transaction = db.transaction([STORE_NAME], 'readwrite');
    const store = transaction.objectStore(STORE_NAME);
    const request = store.delete(fileId);

    request.onsuccess = () => resolve();
    request.onerror = () => reject('Error deleting file');
  });
};

export const getFileById = async (fileId) => {
  if (!db) await initDB();

  return new Promise((resolve, reject) => {
    const transaction = db.transaction([STORE_NAME], 'readonly');
    const store = transaction.objectStore(STORE_NAME);
    const request = store.get(fileId);

    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject('Error getting file');
  });
}; 