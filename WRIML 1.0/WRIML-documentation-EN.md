# WRIML Documentation

## Introduction

WRIML (WRIting Markup Language) is a markup language designed to simplify the writing of textual documents by providing a clear and flexible syntax.

## Principles of Operation

WRIML is based on several fundamental principles for structuring documents:

- **Use of Tags**: Opening and closing tags enclose the content of the document, allowing different elements to be delimited.
  - Example: `^paragraph This is a paragraph _paragraph`
  
- **Simplicity of Syntax**: The syntax of WRIML is simple and intuitive, with tags represented by specific characters.
  - Example: `^heading Section Title _heading`
  
- **Flexibility**: Users can define their own tags and elements according to their specific needs, providing great adaptability.
  - Example: `^note This is a note _note`
  
- **Default Paragraph**: Any text not enclosed by a tag is considered a default paragraph, simplifying the writing process.
  - Example: This is a paragraph without a tag.

## WRIML Syntax

The syntax of WRIML is simple and intuitive. The main elements to remember are:

- **Opening and Closing Tags**: Tags are represented by specific characters, such as `^` for opening and `_` for closing.
  - Example: `^tag Content _tag`
  
- **Empty Tags**: Empty elements are represented by a combination of opening and closing characters, such as `^_tag`.
  - Example: `^br _`
  
- **Attributes**: Attributes are defined using a syntax similar to XML, with the attribute name followed by its value in quotes.
  - Example: `^link_href="https://www.example.com" Link _link`

## Additional Notes

Here are some additional notes on using WRIML:

- **Flexible Tag Names**: Tag names can contain "-" as word separators (e.g., ^tag-name) or use Camel Case convention (e.g., ^TagName).
- **Default Comment Tag**: The default tag for comments is "-", but users can define their own comment tag according to their preferences (e.g., rem, com, note, comment, etc.).
