CREATE TABLE users (
 id SERIAL PRIMARY KEY,
 name VARCHAR(255) NOT NULL,
 email VARCHAR(255) UNIQUE NOT NULL,
 hashed_password VARCHAR(255) NOT NULL,
 created_at TIMESTAMP DEFAULT now() NOT NULL
);
CREATE INDEX ix_users_email ON users (email);

CREATE TABLE projects (
 id SERIAL PRIMARY KEY,
 name VARCHAR(255) NOT NULL,
 description VARCHAR(2000),
 created_at TIMESTAMP DEFAULT now() NOT NULL,
 archived BOOLEAN NOT NULL,
 owner_id INTEGER NOT NULL REFERENCES users(id)
);
CREATE INDEX ix_projects_owner_id ON projects (owner_id);

CREATE TABLE issues (
 id SERIAL PRIMARY KEY,
 title VARCHAR(500) NOT NULL,
 description VARCHAR(5000),
 priority VARCHAR(20) NOT NULL,
 status VARCHAR(20) NOT NULL,
 created_at TIMESTAMP NOT NULL,
 updated_at TIMESTAMP NOT NULL,
 project_id INTEGER NOT NULL REFERENCES projects(id),
 assignee_id INTEGER REFERENCES users(id)
);
CREATE INDEX ix_issues_status ON issues (status);
CREATE INDEX ix_issues_priority ON issues (priority);
CREATE INDEX ix_issues_project_id ON issues (project_id);
CREATE INDEX ix_issues_assignee_id ON issues (assignee_id);
