// MongoDB initialization script
db = db.getSiblingDB('bytepress');

// Create users collection with indexes
db.createCollection('users');

// Create indexes for better performance
db.users.createIndex({ "email": 1 }, { unique: true });
db.users.createIndex({ "created_at": 1 });

print('Database initialized successfully!');
