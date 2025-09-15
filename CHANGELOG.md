# CHANGELOG

<!-- version list -->

## v1.5.0 (2025-09-15)

### Bug Fixes

- Dockers health-check ok
  ([`aee7e5f`](https://gitlab.com/django1361117/recovr_software/-/commit/aee7e5f1a5d860b0a5078c590426c8cf71a2cedd))

### Continuous Integration

- Add self-hosted GitLab runner
  ([`c2e777d`](https://gitlab.com/django1361117/recovr_software/-/commit/c2e777d83253807a304ff1059bb076e6322f26aa))

- Update pyproject.toml to version 1.4.0 [skip ci]
  ([`0265692`](https://gitlab.com/django1361117/recovr_software/-/commit/0265692a5374f3df19dbe9fbcf7a64697837902e))

### Features

- **ci**: Dockers success config health-check ok
  ([`048d108`](https://gitlab.com/django1361117/recovr_software/-/commit/048d1085d331d338aae47e362e2c6cf636b33900))

- **ci**: Succes run self-hosted GitLab runners + format files
  ([`cec3279`](https://gitlab.com/django1361117/recovr_software/-/commit/cec327955d71ebfe113ff8f91779fbba405bf436))


## v1.4.0 (2025-09-14)

### Continuous Integration

- Add $SSH_PRIVATE_KEY to deployement jobs
  ([`bbaa3ea`](https://gitlab.com/django1361117/recovr_software/-/commit/bbaa3ea03e27b5fea8b5f8290d001c8ea0fc8362))

- Add - rsync -e "ssh -i ~/.ssh/id_rsa -o StrictHostKeyChecking=no" -avz --delete \ to deployement
  jobs
  ([`022f7c6`](https://gitlab.com/django1361117/recovr_software/-/commit/022f7c6db9b941cdfe329769cb1a61f5df8e137e))

- Add /.ssh/ before ssh-keyscan
  ([`aa960b5`](https://gitlab.com/django1361117/recovr_software/-/commit/aa960b566d3ef9985c1a4af7763a12d52de1f1c1))

- Add /.ssh/ before ssh-keyscan in deploy-staging job
  ([`41365f2`](https://gitlab.com/django1361117/recovr_software/-/commit/41365f2d82c810fdddd1c0ff04eca49312f6b2fe))

- Add /.ssh/ before ssh-keyscan in deploy-staging job
  ([`fe93cec`](https://gitlab.com/django1361117/recovr_software/-/commit/fe93cec87e0e18987c62595554646edcd1ee1b98))

- Add docker_compose.production.yml docker_compose.proxy.yml docker_compose.staging.yml update
  gitlab-ci.yml and add health url
  ([`0ec23f2`](https://gitlab.com/django1361117/recovr_software/-/commit/0ec23f243d52de7317e3f4e717bdac74d8dbf913))

- CI/CD pipeline and environment configurations
  ([`c7b083a`](https://gitlab.com/django1361117/recovr_software/-/commit/c7b083affa87fe0797987d7cc548a7bcd3b0c3f8))

- Config rsync
  ([`c7c91fe`](https://gitlab.com/django1361117/recovr_software/-/commit/c7c91fe17d20cd61ac93caac16416f0eeb23edf1))

- Config user permissions
  ([`4bfce48`](https://gitlab.com/django1361117/recovr_software/-/commit/4bfce48e98d132ff55c0fb8599299710a1297ecd))

- Enhance Nginx configuration for production and staging
  ([`0c1334b`](https://gitlab.com/django1361117/recovr_software/-/commit/0c1334b913d408baa0a55f024f10f1c0b266df84))

- Reformat .gitlab-ci.yml and health endpoint
  ([`309ec2b`](https://gitlab.com/django1361117/recovr_software/-/commit/309ec2bf1c1d11095f6e808090f0bfb0e15a37bd))

- Reformat .gitlab-ci.yml sync stage
  ([`a9f94ad`](https://gitlab.com/django1361117/recovr_software/-/commit/a9f94ad8147e0295afddcf3c41bc0ecf92471c6e))

- Reformat .gitlab-ci.yml sync stage
  ([`1e55928`](https://gitlab.com/django1361117/recovr_software/-/commit/1e5592850dbec7079b42911837678e721d802399))

- Reformat env file create method
  ([`a80ad7e`](https://gitlab.com/django1361117/recovr_software/-/commit/a80ad7ef2eb6d5d20c1cef4e1e6ee5b29870829e))

- Remove --no-dev option
  ([`6362b01`](https://gitlab.com/django1361117/recovr_software/-/commit/6362b019d9dd975924e48b07e63299c44e08b752))

- Remove apk add replace by apt-get update && apt-get install -y
  ([`f516de5`](https://gitlab.com/django1361117/recovr_software/-/commit/f516de5bcc2e3e58017b5eea29ce313a65ba2879))

- Remove depends_on section
  ([`d5657c3`](https://gitlab.com/django1361117/recovr_software/-/commit/d5657c338287796069029b9af6546871cc61675f))

- Remove nginx deployment in staging and production stage
  ([`ca46d4d`](https://gitlab.com/django1361117/recovr_software/-/commit/ca46d4db92a9b9b86b0638ec173730ea7c08045b))

- Remove nginx deployment in staging and production stage
  ([`30ba4e1`](https://gitlab.com/django1361117/recovr_software/-/commit/30ba4e193bba57d3c14e1a866d593dc74e2e2748))

- Remove nginx deployment in staging and production stage
  ([`e0da5d1`](https://gitlab.com/django1361117/recovr_software/-/commit/e0da5d1f0c1fc00151a06dfbb7dba4bf41ee61f7))

- Remove rsync add docker_compose in deployement method
  ([`b9385e9`](https://gitlab.com/django1361117/recovr_software/-/commit/b9385e94a6e059350673d98eaee9f4a245fe4f33))

- Replace $DO_PROD_IP by $DO_IP
  ([`b67779c`](https://gitlab.com/django1361117/recovr_software/-/commit/b67779c246d8a71a8cab9280449481ad0543133e))

- Update Nginx config and Docker Compose for improved deployment
  ([`38ca7a3`](https://gitlab.com/django1361117/recovr_software/-/commit/38ca7a31a8e440928fdee3e47991dbbc52dac3b5))

- Update Nginx config and Docker setup for staging/production
  ([`0a28bcf`](https://gitlab.com/django1361117/recovr_software/-/commit/0a28bcfe69e96efd091ceb04303bab10c9b574f6))

### Features

- Successfull production deployement
  ([`45b5e59`](https://gitlab.com/django1361117/recovr_software/-/commit/45b5e59635bb5e38812b73149433d49f41a421e0))

- **ci**: Succes deployment jobs deploy-staging deploy-production
  ([`8666e1a`](https://gitlab.com/django1361117/recovr_software/-/commit/8666e1ae0b437a1525d84d7da87507b84ff09c0e))


## v1.3.0 (2025-09-12)

### Bug Fixes

- Ci add option --ignore-installed packaging
  ([`6be3432`](https://gitlab.com/django1361117/recovr_software/-/commit/6be34322b7ebfe21ddc293b6e062c8938fbf4a44))

- Harmonize environment variable names between Docker and Django
  ([`bcaab13`](https://gitlab.com/django1361117/recovr_software/-/commit/bcaab136539e2d7724ed154933b11766d5db0f32))

- Pipeline jobs to run manually by default to test production deployment
  ([`91eedf0`](https://gitlab.com/django1361117/recovr_software/-/commit/91eedf0166bc80e7fa1b35f58727f5ba1e0ad6e9))

- Refactor environment variable names for production setup
  ([`8d9cd8d`](https://gitlab.com/django1361117/recovr_software/-/commit/8d9cd8d3e63497e39a9ebf94d3bc5b36bb29c390))

- Remove default value for PRODUCTION_DB_PORT in docker compose
  ([`6e0b8a0`](https://gitlab.com/django1361117/recovr_software/-/commit/6e0b8a0787ad71671eeaeea142455a0cc9a01e1f))

- Remove redundant default value for DB_PORT in docker_compose.yml
  ([`32f197d`](https://gitlab.com/django1361117/recovr_software/-/commit/32f197d704faddb22f53f44d730b8d7ea0a08e07))

- Simplify deployment script in GitLab CI/CD pipeline
  ([`8e91746`](https://gitlab.com/django1361117/recovr_software/-/commit/8e91746afdbec4191e7ac7d3851ed16568b70469))

- Update CI to use SSH_PRIVATE_KEY for authentication
  ([`85e7a93`](https://gitlab.com/django1361117/recovr_software/-/commit/85e7a939e3058853b2a5925b7da46bd35cd90a3e))

- Update Dockerfile file
  ([`548625b`](https://gitlab.com/django1361117/recovr_software/-/commit/548625b68318d08e9b4113927310113adaa8d829))

- Update environment variable keys in docker_compose.yml
  ([`1f58bf7`](https://gitlab.com/django1361117/recovr_software/-/commit/1f58bf718a56bdfc54f586c682f35396fb1f92c3))

- Update environment variable references in CI and Docker setup
  ([`444d361`](https://gitlab.com/django1361117/recovr_software/-/commit/444d361c81262c5d2291638641f3293e17712687))

- Update poetry.lock file
  ([`30678a4`](https://gitlab.com/django1361117/recovr_software/-/commit/30678a45d82ff13b55bfa1437ef8bbccae57e259))

### Continuous Integration

- Disable 'needs' dependency for production deployment
  ([`1bb2188`](https://gitlab.com/django1361117/recovr_software/-/commit/1bb218823c5d1047b59bbecea49fffcb74599efd))

### Features

- Update to v1.2.0 with CI improvements and environment configs
  ([`ee18d53`](https://gitlab.com/django1361117/recovr_software/-/commit/ee18d532ee0c3a1bd78166fb9d37f14f0b88cfad))

- **ci**: Add production deployment pipeline
  ([`83af926`](https://gitlab.com/django1361117/recovr_software/-/commit/83af926b5481ad583d4ba1c8eef29bc26759e5a3))

### Refactoring

- Poetry.lock from Dockerfile COPY instruction
  ([`6d4147f`](https://gitlab.com/django1361117/recovr_software/-/commit/6d4147f3737bb5ef49a0208dff5f034b3ae639ba))

- Production deployment pipeline in .gitlab-ci.yml
  ([`b3c8351`](https://gitlab.com/django1361117/recovr_software/-/commit/b3c8351f1869e58ec7f6eb71c568db83c0d67948))

- Remove --no-update flag from poetry lock command
  ([`881c4e3`](https://gitlab.com/django1361117/recovr_software/-/commit/881c4e3d4107653a104f9368c8b303edc9ad7bb3))


## v1.2.0 (2025-09-10)

### Bug Fixes

- .gitlab-ci.yml to specify Docker Compose file path
  ([`b4c53ec`](https://gitlab.com/django1361117/recovr_software/-/commit/b4c53ec1313a7e04ef7e5265ac1e4e12c9340c90))

- Add __init__.py to initialize the package
  ([`2cc826e`](https://gitlab.com/django1361117/recovr_software/-/commit/2cc826e96c129739c094da40c0dc8f81f146a74a))

- Add env file to docker-compose command
  ([`ae56aef`](https://gitlab.com/django1361117/recovr_software/-/commit/ae56aef4efa7de1f83dd69cb5d721d5796f0030b))

- Add manual triggers and improve deployment configuration
  ([`e625f1a`](https://gitlab.com/django1361117/recovr_software/-/commit/e625f1abd78f834d4308fc72b7fc24917038c8ea))

- CI to use environment variables for dynamic configuration
  ([`1a5dda0`](https://gitlab.com/django1361117/recovr_software/-/commit/1a5dda0b36f3072affb7309ec5b842172166ebd7))

- Correct docker-compose syntax in deployment script
  ([`6b98046`](https://gitlab.com/django1361117/recovr_software/-/commit/6b98046d58bafe83b331056359e016dab3c75dc8))

- Correct docker-compose syntax in deployment script
  ([`94ff5d3`](https://gitlab.com/django1361117/recovr_software/-/commit/94ff5d3a915a910d11fae6ba8b85491571bfbf44))

- Correct path to Nginx config in staging deployment
  ([`91c0cb5`](https://gitlab.com/django1361117/recovr_software/-/commit/91c0cb512fe9aa58560f04fd1990c22ce83057fc))

- Docker-compose
  ([`561bf76`](https://gitlab.com/django1361117/recovr_software/-/commit/561bf76e648e9fb21c8c7a9e96fc7a02a9ba3ee1))

- Environment file for dynamic configuration
  ([`e99c85e`](https://gitlab.com/django1361117/recovr_software/-/commit/e99c85ea7ca7610d6ae41f35e2757d4cae58b7dc))

- Environment file for dynamic configuration
  ([`d2117d7`](https://gitlab.com/django1361117/recovr_software/-/commit/d2117d763b3445daa5e573c4eeebf4fffe5e851f))

- Environment file for dynamic configuration
  ([`e7ea3ac`](https://gitlab.com/django1361117/recovr_software/-/commit/e7ea3ac0daf03b65be766ed556be5f44c39e6f3e))

- Environment file for dynamic configuration
  ([`10591c8`](https://gitlab.com/django1361117/recovr_software/-/commit/10591c809bf7d6234b867e99cb7fc39068ce7d7c))

- Environment file for dynamic configuration
  ([`468fbe4`](https://gitlab.com/django1361117/recovr_software/-/commit/468fbe4f77f0e140420098eb70116eb439d5369f))

- Environment file for dynamic configuration
  ([`1d4929e`](https://gitlab.com/django1361117/recovr_software/-/commit/1d4929ed70427a6c74b3c35c1cfcf17cc03853ce))

- Environment file for dynamic configuration
  ([`768d117`](https://gitlab.com/django1361117/recovr_software/-/commit/768d117de8413c25544554197d3adf0b9b32b4ba))

- Environment file for dynamic configuration
  ([`d358581`](https://gitlab.com/django1361117/recovr_software/-/commit/d358581254690e96f0179f7785e5f2bf5575ba1d))

- Environment file for dynamic configuration
  ([`783217a`](https://gitlab.com/django1361117/recovr_software/-/commit/783217a2b33d1b6a63b2f254c17dd2cc08772cd9))

- Environment file for dynamic configuration
  ([`32a6b4d`](https://gitlab.com/django1361117/recovr_software/-/commit/32a6b4d5fe5a16b95c40a7683c1434fb74de1ae5))

- Environment file for dynamic configuration
  ([`4688392`](https://gitlab.com/django1361117/recovr_software/-/commit/4688392b5bd0812befbcd32c89589fc01285b936))

- Environment file for dynamic configuration
  ([`5b1324c`](https://gitlab.com/django1361117/recovr_software/-/commit/5b1324ce96ec6409af47355e32564ca3214edc1e))

- Environment file for dynamic configuration
  ([`342a8d7`](https://gitlab.com/django1361117/recovr_software/-/commit/342a8d7ca64197784e6798b26dddd5e45bc85ba1))

- Environment file for dynamic configuration
  ([`7b2494f`](https://gitlab.com/django1361117/recovr_software/-/commit/7b2494f47020e9ba474ccbee39eb46fc52ea3400))

- Environment file for dynamic configuration
  ([`7fa675a`](https://gitlab.com/django1361117/recovr_software/-/commit/7fa675ac5f9af9ce888afa1e1aa7674cd37e661f))

- Environment file for dynamic configuration
  ([`857e5d9`](https://gitlab.com/django1361117/recovr_software/-/commit/857e5d9ab54f02c09178921ed86dfaf4e2b98ccb))

- Environment file for dynamic configuration
  ([`a803f8d`](https://gitlab.com/django1361117/recovr_software/-/commit/a803f8df06cbe4e332f6ad0d8658f6254f616d9f))

- Environment file for dynamic configuration
  ([`f1bab24`](https://gitlab.com/django1361117/recovr_software/-/commit/f1bab24c85e0e8e3a1ade9ff5f73b12274612e04))

- Environment file for dynamic configuration .env.staging -> .env
  ([`c44a9b3`](https://gitlab.com/django1361117/recovr_software/-/commit/c44a9b3c002085826749d51f6009093c4743bdb1))

- Poetry package installation in CI pipeline
  ([`55fe9c1`](https://gitlab.com/django1361117/recovr_software/-/commit/55fe9c15efb5a090ac5b0951c68480e243e0bc54))

- Resolve only/rules conflict in CI configuration
  ([`c387145`](https://gitlab.com/django1361117/recovr_software/-/commit/c38714595bb75ed94c9c7392e736346e786e4c5c))

- Simplify and fix SSH configuration in GitLab CI.
  ([`04152d9`](https://gitlab.com/django1361117/recovr_software/-/commit/04152d9194e9f3d78ca3c9ae7af24e292f48e3ac))

- Update Poetry install command to include --no-root option
  ([`a85cfda`](https://gitlab.com/django1361117/recovr_software/-/commit/a85cfdacd16d69ebb6666548861baa15beaea658))

- **ci**: Improve SSH connection reliability in deployment jobs
  ([`18df6f2`](https://gitlab.com/django1361117/recovr_software/-/commit/18df6f29f2a018d97d70aa0a130462a9c5cb4078))

### Continuous Integration

- Add Gunicorn and update CI SSH key setup
  ([`7efeacc`](https://gitlab.com/django1361117/recovr_software/-/commit/7efeacc462aa748f4f8762d14c1cfb4fa51c263a))

- Add Gunicorn and update CI SSH key setup
  ([`a0494b9`](https://gitlab.com/django1361117/recovr_software/-/commit/a0494b94a1259e4dedbfd9ef5e43aa9ebc925406))

- Add separate stages for staging and production deployment
  ([`b2668d7`](https://gitlab.com/django1361117/recovr_software/-/commit/b2668d7509e9b3906841eb74b27e8a17616047d5))

- Automate pipeline jobs and prepare for production deployment
  ([`2fd2ce3`](https://gitlab.com/django1361117/recovr_software/-/commit/2fd2ce39dc2a5b83c2ed8d39a969d76e797f590c))

### Features

- Add Docker basic configuration
  ([`6ca19b7`](https://gitlab.com/django1361117/recovr_software/-/commit/6ca19b72306124c8f5ee2e49422c4baffbf75439))

- Configure PostgreSQL for local development environment"
  ([`acdcf4d`](https://gitlab.com/django1361117/recovr_software/-/commit/acdcf4d74bc3c6e5dfc7848aa2b79af93bd49f57))

- Implement Docker-based deployment for staging environment
  ([`1be6107`](https://gitlab.com/django1361117/recovr_software/-/commit/1be61071b2abfb5e2b7bbc2d19fef0cf8c5fee89))

- Successful staging deployment
  ([`2f99b1f`](https://gitlab.com/django1361117/recovr_software/-/commit/2f99b1f406000178124aad266d5229e218a1bc75))

- Successful staging deployment
  ([`fcac5f5`](https://gitlab.com/django1361117/recovr_software/-/commit/fcac5f55ac0f34a8f9151b4b147631a236ffdb62))

- Successful staging deployment
  ([`5b53531`](https://gitlab.com/django1361117/recovr_software/-/commit/5b535311215cf9a08ef195c454331ceb6bd12bcd))

- Update NGINX configs and CI/CD pipelines for new domains
  ([`3935c03`](https://gitlab.com/django1361117/recovr_software/-/commit/3935c03347defe43f6a8d8002cd35875c3cdcce5))

- **infra**: Add Nginx configuration for production and staging environments
  ([`4c0d090`](https://gitlab.com/django1361117/recovr_software/-/commit/4c0d09082ba50c43732a44cef79f90dd0c282876))

### Refactoring

- Settings for environment-specific configurations
  ([`7e375db`](https://gitlab.com/django1361117/recovr_software/-/commit/7e375db72243aba374c062027669b3a471e42854))


## v1.1.0 (2025-09-03)

### Bug Fixes

- Add GitHub token to Github deployment
  ([`2e166f1`](https://gitlab.com/django1361117/recovr_software/-/commit/2e166f1c1372ab50069d45ec57cdeefbc91a2149))

- Add GitHub token to semantic-release configuration
  ([`25d5279`](https://gitlab.com/django1361117/recovr_software/-/commit/25d527992729ad620c4780dc59fbbfff1b82c108))

- Configure semantic-release to use GitLab instead of GitHub
  ([`0c3d987`](https://gitlab.com/django1361117/recovr_software/-/commit/0c3d98797973f421dcffe36351c42c25714760dd))

- Convert SSH key to PEM format
  ([`3851ed8`](https://gitlab.com/django1361117/recovr_software/-/commit/3851ed806dfb4909f0996b5f1c5773c9c4c72ed2))

- Improve CI pipeline debugging and error handling
  ([`e3df770`](https://gitlab.com/django1361117/recovr_software/-/commit/e3df7708292c3657b3d116054b0acf7473c70696))

- **ci**: Correct GitHub sync SSH key configuration
  ([`ecf0c71`](https://gitlab.com/django1361117/recovr_software/-/commit/ecf0c71d40d4aefc30ff187ae5e7ab28bfd0a4cf))

- **ci**: Correct semantic-release command syntax
  ([`384a459`](https://gitlab.com/django1361117/recovr_software/-/commit/384a45968f39031634b3048cd585867d6de2fa0f))

- **ci**: Correct YAML syntax in .gitlab-ci.yml
  ([`ccdfe64`](https://gitlab.com/django1361117/recovr_software/-/commit/ccdfe64c1b130c800141466dbb0d69de45e3ca4c))

- **ci**: Restore functional CI/CD pipeline
  ([`c0b28d2`](https://gitlab.com/django1361117/recovr_software/-/commit/c0b28d24248a3569e36fdb2c0dd0dd9f4da72ce5))

- **ci**: Restore functional CI/CD pipeline
  ([`d77ce80`](https://gitlab.com/django1361117/recovr_software/-/commit/d77ce80db5d05720e88cc5fbd0fa4f18bf22cf29))

- **ci**: Use SSH auth for Git clone operations
  ([`1dfaddc`](https://gitlab.com/django1361117/recovr_software/-/commit/1dfaddc1c49d8d6f795bad087025f4186c2639c2))

### Chores

- Remove IntelliJ-specific files and project documentation
  ([`c71aeff`](https://gitlab.com/django1361117/recovr_software/-/commit/c71aeff8fe44b282feb3341ee4c3e2bf25f1ea67))

### Continuous Integration

- Improve pyproject.toml file handling
  ([`4c8ddd3`](https://gitlab.com/django1361117/recovr_software/-/commit/4c8ddd3e955ff5ae583785e76e920da8dc82afa5))

### Documentation

- Add semantic-release instructions to README
  ([`b8e2e11`](https://gitlab.com/django1361117/recovr_software/-/commit/b8e2e11d5793aa9cc1f1d14c2587bff2ff41a91a))

### Features

- Initialize project structure
  ([`1f805c4`](https://gitlab.com/django1361117/recovr_software/-/commit/1f805c41be4794d154f9b28a34404f428ee12583))


## v1.0.0 (2025-09-02)

- Initial Release
