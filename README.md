# Marvel Superhero Search

## Description

The goal of this site is to allow users to search for their favorite Marvel Comics Characters. The site will provide information such as, character name, a brief description of the character, and comic appearances. Users will also be able to keep track of their favorite characters by adding them to a favorites list.

The site is deployed on Heroku and can be found [here](https://marvel-char-search.herokuapp.com/signup)

## Data Source / API

The Marvel Developer Portal [API](https://developer.marvel.com/) was used to get all the character, comic, and creator information for this site.

The tech stack is a Python back end using Flask, with server rendered jinja pages. There is minimal JavaScript, the database is handled through Flask-SQLAlchemy interfacing for PostgreSQL, and form validation through WTForms.

## Functionality

- Create user profile
- Search for specific character
- Add characters to a favorites list

## User Flow

1. Landing Page - Signup/Login to user account.
2. User Sign-Up Page - Allows user to create personal profile/account.
3. User Login Page - Allows user to login to existing profile/account.
4. Character Page - Allows user to search for characters and add to favorites list.
5. Users Profile Page - User can see their information as well as favorites list.
