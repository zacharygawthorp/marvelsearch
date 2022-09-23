# Marvel Superhero Search

## Goal

This Flask web application will allow users to search for their favorite Marvel Comics Characters. The app will provide information such as, character name, a brief description of the character, and comic appearances. Users will also be able to keep track of their favorite heroes by adding them to a favorites list.

## Demographic

There is no specific target demographic for this application as anyone from any race/ethnicity or age could enjoy using it.

## Data Source / API

I plan on pulling character stats from the Marvel Developer Portal API https://developer.marvel.com/

## Schema

![schema-table](images/schema-table.png)


## Potential Issues

API has a limit on the number of calls per day, however it is a large number. 

## Sensitive Information

Encrypted passwords will be stored for the user model.

## Functionality

* Search for specific character
* Create user profile
* Add characters to a favorites list

## User Flow

1. Landing Page - Signup/Login to user account. 
2. User Sign-Up Page - Allows user to create personal profile/account.
3. User Login Page - Allows user to login to existing profile/account.
4. Character Page - Allows user to search for characters and add to favorites list.
5. Users Profile Page - User can see their information as well as favorites list.

## Stretch Goals

* Ability to see who the creator of the comics are. 