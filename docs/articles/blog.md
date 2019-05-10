# Surround

*The framework used by the Applied Artificial Intelligence Institute (A<sup>2</sup>I<sup>2</sup>) to build, deploy and handover machine learning projects to clients.*

**TLDR;** Surround is a framework developed by A<sup>2</sup>I<sup>2</sup> to take machine learning projects from concept through to production. Surround is designed to play nice with existing machine learning frameworks (Tensorflow, MXNet, PyTorch etc.) and cloud services (Google Cloud AI, SageMaker, Rekognition etc.) We designed Surround for software engineers and research engineers*, and is suitable for a range of deployment scenarios (offline, internal infrastructure, or in the cloud).

AI is an emergent opportunity for businesses. However, it introduces new challenges for us to overcome, such as support for the journey from prototype to production. A<sup>2</sup>I<sup>2</sup> is Australia's largest AI institute recently formed at Deakin University. Our team specialises in building early stage prototypes that are transferred to industry for evaluation and ongoing support. Due to the variety and number of projects we work on (more details [here](http://a2i2.ai)) we needed a flexible and consistent way to organise our machine learning projects. Surround was developed to help improve **evaluation and field testing**, **reliability**, **maintainability**, **reproducibility**, and **consistency** in our projects.

Surround is now available to the community for feedback and is actively being developed [http://github.com/dstil/surround](http://github.com/dstil/surround).

## Motivation

**Huge effort is required to deploy an early prototype into a production environment**

Typically, a project is first given to a research engineer to develop the initial solution (prepare the data, select an appropriate algorithm, train a model, evaluate the approach etc.) A software engineer is then tasked with preparing the scripts for integration and deployment into a client's environment. We found concerns such as the handling of configuration for development, staging and production environments, the format and location of log files, whether a queue or web interface will be used, and so on, all influence the implementation of the initial solution. These concerns are not paramount to research engineers who do not typically come from an engineering background, but a scientific background. It is time consuming to repeatedly reconcile these differences in design and implement for each project.

**Maintaining a production-grade machine learning system is hard**

Over time we realised that clients were finding it difficult to maintain and support such complex pieces of technology. We also noticed that while each solution is unique there are many aspects which are the same but that there are no opensource convention based frameworks for developing machine learning projects. Unlike say web development which abounds in frameworks such as Ruby on Rails, Spring Boot, Laravel, Django etc. We hope to build a community around Surround that is focused on building best practices into a single framework to improve the quality of the systems we build and increase developer productivity.

**Lack of consistency between machine learning projects**

At A<sup>2</sup>I<sup>2</sup> the focus is on delivering a *solution* that can be trialled by a client whether the solution leverages cutting edge research or techniques developed 20 years ago. This flexibility means that projects have different libraries and dependencies which all need to be bundled together for deployment. Another observation from our projects, is that each team had their own approach to a problem and were often reinventing the solutions. Reproduceability was challenging as each project handled data and model management slightly differently. While partly a process issue part of the solution relies on the technical implementation. There was also no consistent way to train, build, debug and deploy each project as our client's have varied requirements from running offline on multiple desktops to embedded behind corporate firewalls. Each machine learning project also requires configuration, model management, training data and experimentation yet each project tackles these problems in their own unique way.

## What is Surround?

We built Surround to help us with the challenges outlined above. The Surround framework consists of four core elements a philosophy, a set of conventions, a command line tool and a Python library.

### A Philosophy

**Exploration to Production**

From the moment data lands on our desk we need to be thinking about the final use case for the solutions we are developing. We built Surround to help us move from data exploration to a containerised proof-of-concept web application ready to deploy in the shortest time possible. To do this we needed to resolve the competing requirements of researchers and engineers. For example, researchers want to dive into the data leaving code quality for later where as engineers want well structured code from the start. We solved this problem by focusing the team on a "production first" mindset and through a convention (data exploration scripts had their own folder). At times small compromises needed to be made to ensure that everyone can use Surround for their use cases.

**A Place For Everything**

Web frameworks have realised long ago that there are a set of concerns that web applications must deal with such as connecting to databases, managing configuration, rendering static and dynamic content, and handling security concerns. Similar concerns need to be handled by machine learning projects but there are also specific concerns such as experimentation is a first class citizen, data and models need to be versioned and managed, model performance needs to be visualised, training infrastructure is required etc. Surround strives to provide a single place for every concern that arises when building a ML project. The concerns can face either the software engineer or research engineer and ideally there will only be a single solution for handling that problem. In situations where Surround does not support particular functionality it should be obvious how to add it.

**Play Nice With Others**

There are many good existing frameworks, libraries and APIs that research engineers can use to build a solution. Surround should strive to integrate nicely with as many of these 3rd party solutions as possible. This is reflected in the design of Surround where the core framework could be used to build: a solution based on cloud APIs, a custom Docker image for SageMaker or form part of a batch process running on an internal Kubernetes cluster. Research engieners also use different tools such as Jupyter notebooks which have a place in a Surround project (see below). By playing nice with others we hope the core Surround framework can continue to be used as the ML ecosystem continues to improve.

**Familiarity**

Many of the design guidelines and tools are heavily inspired by other frameworks such as Spring Boot for configuration management, Tensorflow serving for endpoint definition and the git command line tool for Surround's CLI. We made this a core philosophy to ensure both software engineers and research engineers can quickly get started with Surround. At times this was a challenge as Surround is a framework designed explicitly for two different types of people a traditional software engineer and a science focused research engineer.

### A set of conventions

**Project layout**

All the ML projects have the following conventions in common, requirement on data, monitor progress output, load models, and manage configuration. Surround introduces conventions for all four concepts to ensure that research engineers do not have to concern themselves with how these features will work. As our ML projects are written in Python we leverage Python package conventions for consistency. These conventions are adhered to through a project generator and project linter that checks for the core conventions.

Surround implements the following directory structure:

<pre>
package name
├── Dockerfile
├── README.md
├── data
├── package name
│   ├── __main__.py
│   ├── config.yaml
│   ├── visualiser.py
│   ├── loader.py
│   └── stage
│       ├── validator.py
│       ├── wrangler.py
│       ├── decider.py
│       └── estimator.py
├── docs
├── dodo.py
├── models
├── notebooks
├── output
├── requirements.txt
├── scripts
├── spikes
└── tests
    └── integration.py
</pre>


Each Surround project has the following characteristics:

- Dockerfile for bundling up the project as a web application.
- dodo.py file containing useful tasks such as train, batch predict and test for a project.
- Tests for catching training serving skew.
- A single entry point for running the application, __main__.py.
- A place for data exploration with Jupyter notebooks and miscellaneous scripts.
- A single place, for output files, data, and model storage.

**Choice of integration**

Most of the functionality provided by Surround is through a careful curated set of dependencies that work seemlessly together. Another guiding factor to Surround was to mine ideas and solutions from real-world projects. For example, we decided to make [Tornado][https://www.tornadoweb.org/en/stable/] the default web application in Surround over the popular Flask framework. This decision was based on needing to stream video over TCP for a face recognition project and Tornado with it's asynch IO model proved a better fit (replacing Tornado is as simple as removing the dependency from the generated requirements.txt file in a new Surround project!) We also use Docker in a Surround project to make sure that everything can be run in multiple environments and to simplify DevOps related issues. Another choice we made was to integrate doit (makefiles were also considered but some of our clients are on Windows) as a build for Surround. We found that there were always tasks that needed to be run as part of a project such as, running tests, training a model, analysing model responses, generating visualisations etc. Many of these tasks can be called from a single script which means every new person on the project knows where to look to make modifications.

### A command line tool

Surround also includes a couple of light weight tools bundled together to help manage a Surround project. The core tools of Surround are as listed below:

- `init` - Used for generating a new Surround project.
- `run` - Used for running a task on Surround and for starting the webserver.
- `lint` - Used to check that Surround conventions are being followed.

We developed, run as a wrapper around doit so that every project can use `surround run` to find out what tasks are available for the current project. We also developed a linter to help guide developers with the best practices when it comes to ML. Our intention is to greatly expand the linter to be more of an assistant for building a ML project.  Internally, we are also working on an extension of the existing toolchain to manage data and models (whether they be trained on a GPU cluster, on local machines or on a Cloud Service).

### A Python library

Finally, the last component of Surround is the Python library. We developed the Python library to provide a flexible way of running a ML pipeline in a variety of situations whether that be from a queue, a http endpoint or from a file system. We found that during development the research engineer often needed to run results from a file, something that is not always needed in a production environment. Surround's Python library was designed to leverage the conventions outlined above to provide maximum productivity boost to research engineers provided the conventions are followed. Surround also provides wrappers around libraries such as the Tornado web server to provide advanced functionality. These 3rd party dependencies are not installed by default and need to be added to the project before Surround will make the wrappers available.

## Existing Case Studies

While Surround is still under heavy development early versions are proving to be extremely useful. Surround is currently used on the following projects:

- **Face recognition for catching exam cheats in India.** Surround was used to wrap a face recognition pipeline consisting of 5 machine learned models and used on 480,000 students to find exam cheats. The system was deployed offline, operated as a batch processor over a directory of photos and scaled by starting multiple processes on different desktop computers.
- **Reading marathon runner bibs.** Surround was used to build a pipeline leveraging a pre-trained model and a Google Cloud API for optical character recognition. This application connected to AWS S3 for reading images and connected to a queue so multiple workers could be started. A web application was built independently of the Surround micro-service to provide a dashboard for admin tasks.
- **Detecting falls in aged care facilities.** Video feeds from security cameras were analysed to identify when elderly people had a fall. Surround was used to implement the feature extraction steps and logic for triggering an alarm when a fall was detected.
- **Email classification for business processes.** A recent project leveraged Surround to process emails one at a time. Surround was used to train a custom model, and a batch mode used to verify the results achieved in production offline.
- **Fraud detection in insurance.** Surround was used to build the core logic of a fraud detection system and deployed to the cloud for evaluation by our client. Currently under development.

## What's next?

We are still working hard towards a version 1.0 for Surround but really need your feedback. Please checkout Surround and get in touch with us directly or leave feedback on the Github page. Stay tuned for more blog posts about this project!

## Acknowledgements

Thank you to the clients that worked with us and helped provide feedback on our project which ultimately guided the development of Surround.

TODO People


* Throughout this article I refer to Research Engineers rather than Data Scientists. Research engineers are expected to contribute to building a working prototype rather than pure Data Science related work. At A<sup>2</sup>I<sup>2</sup> we have software engineers who are responsible for developing the application and DevOps related tasks. The research engineers are responsible for data analysis and model training.
