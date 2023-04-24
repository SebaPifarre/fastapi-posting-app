# Web App for Uploading Posts

This repository contains a web application for uploading posts. The application is built using the FastAPI framework and uses JWT for authentication. The data is stored in a PostgreSQL database hosted on elephantSQL and SQLAlchemy is used as the ORM.
I deployed the app using deta, you can follow the link to try the app yourself [https://fastapi_pifarre-1-t8668309.deta.app/] or look at the documentation at [https://fastapi_pifarre-1-t8668309.deta.app/docs]

## API Endpoints

The following API endpoints are available in the application:

- `GET /posts`: Get a list of all posts
- `GET /posts/{id}`: Get a post by ID
- `POST /posts`: Create a new post
- `PUT /posts/{id}`: Update a post by ID
- `DELETE /posts/{id}`: Delete a post by ID
- `POST /login`: Authenticate a user and get a JWT token

## Built With

- [FastAPI](https://fastapi.tiangolo.com/) - The web framework used
- [JWT](https://jwt.io/) - The authentication method used
- [PostgreSQL](https://www.postgresql.org/) - The database used
- [SQLAlchemy](https://www.sqlalchemy.org/) - The ORM used

## Authors

- Ricardo Sebastián Pifarré - [https://fastapi_pifarre-1-t8668309.deta.app]

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
