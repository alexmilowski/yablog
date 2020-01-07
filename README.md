# yablog

A simple YAML-based blog entry format.

## Motivation

In 2016, I was motivated to make my blog and website easier. I wanted to use "Semantic Web" technology and drive the blog for my website and other content by the "linked data graph". That project, called [duckpond](https://github.com/alexmilowski/duckpond/) worked well.

During the process, I wanted a simple authoring format where I could use github to store my blog entries and associated artifacts safely. Markdown seemed like a good choice except that I also needed a way to author the metadata. Originally, I settled on a simple header format of key/values. Ultimately, this has evolved into the use of YAML.

Turns out that Markdown nicely embeds into YAML. Who knew?

## An Example

Every entry parses as a YAML file. The essential metadata map nicely to a [schema.org BlogPosting](http://schema.org/BlogPosting) type although the properties are not named extactly the same.  For example, the following is an entry off my website.

```YAML
title: SF Microservices Meetup - Going Serverless with Flask
author: Alex Miłowski
published: 2017-07-12T10:35:00-07:00
updated: 2017-07-12T10:35:00-07:00
keywords:
- python
- Flask
- Serverless
content: |
   I built a python package (see: [https://github.com/alexmilowski/flask-openwhisk](https://github.com/alexmilowski/flask-openwhisk)) for bridging between WSGI (Flask) and [OpenWhisk](http://openwhisk.incubator.apache.org). I have only tested it with Flask but it should work with
   other WSGI frameworks.

   The key takeaway is that you can deploy Flask applications with minimal changes on Serverless. Any
   changes that are necessary have to do with architectural changes for Serverless infrastructure. That
   typically comes from the fact that there is no local environment so configuration or
   local resources (e.g., files) need to be handled differently.
```

## Format Description

## Parsing with Python

This repository contains a python package for parsing the entries and transforming them into various formats: HTML, Turtle, JSON-LD.
