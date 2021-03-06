/**
 * Created by Hope on 6/18/2016.
 */
'use strict';   // See note about 'use strict'; below

var myApp = angular.module('myApp', []);

myApp.controller('MyCtrl', MyCtrl)
    .controller('HomeCtrl', HomeCtrl)
    .controller('FeedCtrl', FeedCtrl)
    .directive("graphDirective", function () {
        return {
            template: ""
        };
    })
    .factory("FeedService", function ($http) {

    })
    .factory("jsService", function () {
        // here goes the code of your js (d3 in my case)
        //now return the object of the service

        return d3;
    });

function FeedCtrl($scope, $http) {
    $scope.websites = [
        {title: "Top", content: "Top content"},
        {title: "Genomeweb", content: "Genomeweb content"},
        {title: "FierceBiotech", content: "FierceBiotech content"},
        {title: "SynBioBeta", content: "SynBioBeta content"},
        {title: "Labiotech", content: "Labiotech content"},
        {title: "reddit", content: "reddit content"},
        {title: "Xconomy", content: "Xconomy content"},
        {title: "Twitter Lists", content: "Twitter Lists content"},
        {title: "Biostars", content: "Biostars content"},
        {title: "Google Scholar", content: "Google Scholar content"},
        {title: "Suggest a Source", content: "Suggest a Source content"}
    ];
    var faketitles = [
        {
            title: 'fakeTitle',
            link: "link",
            outlets: [{name: "title1", img: "image", link: "newslink"}, {
                name: "title1",
                img: "image",
                link: "newslink"
            }]
        },
        {title: 'fakeTitle', link: "link", outlets: [{name: "title2", img: "image", link: "newslink"}]},
        {title: 'fakeTitle', link: "link", outlets: [{name: "titl3e", img: "image", link: "newslink"}]},
        {title: 'fakeTitle', link: "link", outlets: [{name: "title4", img: "image", link: "newslink"}]},
        {title: 'fakeTitle', link: "link", outlets: [{name: "title5", img: "image", link: "newslink"}]},
        {title: 'fakeTitle', link: "link", outlets: [{name: "title6", img: "image", link: "newslink"}]},
        {title: 'fakeTitle', link: "link", outlets: [{name: "title7", img: "image", link: "newslink"}]},
        {title: 'fakeTitle', link: "link", outlets: [{name: "title8", img: "image", link: "newslink"}]}
    ];
    // $scope.content = $scope.websites[0].content;
    $scope.content = faketitles;

    $scope.switchContent = function (selected) {
        // var data = getRecentCrawl(selected.title);
        $http({
            url: '/thenewsfeed',
            method: "POST",
            headers: {'Content-Type': 'application/json'},
            data: JSON.stringify(selected.title)
        }).then(function (response) {
            console.log(response);
            $scope.responseobject = response.data.objects;
            $scope.content = $scope.responseobject;
        });

    }


}
function HomeCtrl($scope, $window) {
    $scope.q1 = false;
    $scope.q2 = false;
    $scope.q3 = false;
    $scope.q4 = false;
    $scope.q5 = false;
    $scope.q6 = false;

    $scope.switchFaq = function (q) {
        // console.log(q);
        q = q ? false : true;
    }
}
function MyCtrl($scope, $http, $window) {


    $scope.catbool = "";
    $scope.some_data =
    {
        "nodes": [],
        "edges": []
    };
    $scope.config = {
        dataSource: $scope.some_data
    };

    $scope.suggestedMatches = [];
    $scope.alchemy = new $window.Alchemy($scope.config);

    $scope.matchmade = false;
    $scope.explorebool = false;
    $scope.connected = true;
    $scope.userOneBool = false;
    $scope.userTwoBool = false;
    $scope.samplescore1 = 24;
    $scope.samplescore2 = 95;
    $scope.sampletags = [
        "Zika", "IBM", "Watson",
        "Biotech", "Genetics", "Amurrica",
        "SynBio", "Python", "Testing",
        "DNA", "BioBreaks", "Life"
    ];
    $scope.selectDisabled = "disabled";
    $scope.exploretext = "View Messages";
    $scope.explorecurrent = "Messages";
    $scope.currentEntities = [
        {img: "static/img/place_holderpic.png", name: "channel1"}
    ];
    $scope.typeOptions = [
        // {name: 'Explore by User', value: 'user'},
        {name: 'Explore by Tag', value: 'tags'}
        // {name: 'Explore by Intent', value: 'bug'},
        // {name: 'Explore by Type', value: 'enhancement'}
    ];
    $scope.channels = [
        {name: 'Channel 1', value: 'feature'},
        {name: 'Channel 1', value: 'feature'},
        {name: 'Channel 1', value: 'feature'},
        {name: 'Channel 1', value: 'feature'}
    ];
    $scope.form = {type: $scope.typeOptions[0].value};
    $scope.responseobject = "RESPONSE OBJECT GOES HERE";
    $scope.graphstyle = "background-color:rgba(0, 0, 0, 0.5) !important;";
    $scope.graphstatebool = false;


    $scope.switchExplore = function () {
        // console.log($scope.connected);
        $scope.connected = true;
        $scope.explorebool = !$scope.explorebool;
        $scope.exploretext = $scope.explorebool ? "View Graph" : "View Messages";
        $scope.explorecurrent = !$scope.explorebool ? "Graph" : "Messages";

    };
    $scope.switchConnect = function () {
        $scope.connected = !$scope.connected;
        // console.log($scope.connected)
    };
    $scope.switchCatSelection = function (entity) {
        $scope.userOne = entity;
        $scope.userOneBool = true;
        if ($scope.connected)
            $scope.getGraphData(entity.id);
        else
            $scope.getUserOneData(entity.id);
        // console.log(entity);
        if ($scope.userOneBool && $scope.userTwoBool) {
            $scope.selectDisabled = "";
        }

    };
    $scope.switchConnectInner = function () {
        $scope.matchmade = !$scope.matchmade;
    };
    $scope.testAPI = function () {
        $http({
            method: 'GET',
            url: '/api/getchannels'
        }).then(function successCallback(response) {
            // $scope.responseobject = response.data;
            $scope.channels = [];
            // console.log(response);
            // $scope.channels.push({img: "None", name: "All Channels"});
            response.data.channels.forEach(function (channelobj) {
                $scope.channels.push({img: "None", name: channelobj.name});
            });
        }, function errorCallback(response) {
            // called asynchronously if an error occurs
            // or server returns response with an error status.
            console.log(response)
        });
    };
    $scope.msgFilter = function (message) {
        return message.type === "messages";
    };
    $scope.getUsers = function () {
        var url = "";
        if ($scope.catbool == "") {
            url = '/api/getcategories';
            // console.log($scope.catbool);
            $http({
                method: 'GET',
                url: url
            }).then(function successCallback(response) {
                $scope.responseobject = response.data;
                $scope.currentEntities = [{img: "/static/img/place_holderpic.png", name: "All Users", id: "All"}];
                // console.log(response);
                // $scope.channels.push({img: "None", name: "All Channels"});

                $scope.suggestedMatches = [];

                getNewMatches($scope.responseobject);

                response.data.members.forEach(function (member) {
                    $scope.currentEntities.push({
                        img: member.profile.image_32,
                        imglg: member.profile.image_48,
                        name: member.name,
                        id: member.id
                    });

                });
                // console.log($scope.currentEntities)
            }, function errorCallback(response) {
                // called asynchronously if an error occurs
                // or server returns response with an error status.
                // console.log(response)
            });
        } else if ($scope.catbool == "tags") {
            url = '/api/gettags';
            $http({
                method: 'GET',
                url: url
            }).then(function successCallback(response) {
                $scope.currentEntities = [{img: "/static/img/place_holderpic.png", name: "All Users", id: "All"}];
                console.log(response);
                // $scope.channels.push({img: "None", name: "All Channels"});
                var i;
                $scope.suggestedMatches = [];
                for (i = 0; i < 5; i++) {

                    var p1 = response.data.members[Math.floor(Math.random() * response.data.members.length)];
                    var p2 = response.data.members[Math.floor(Math.random() * response.data.members.length)];
                    $scope.suggestedMatches.push(
                        {
                            "user1": {
                                "img": p1.profile.image_32,
                                "name": p1.name,
                                "id": p1.id
                            },
                            "user2": {
                                "img": p2.profile.image_32,
                                "name": p2.name,
                                "id": p2.id
                            }
                        });
                }

                response.data.nodes.forEach(function (tag) {
                    $scope.currentEntities.push({img: "/static/img/place_holderpic.png", name: tag.value, id: tag.id});

                });
                // console.log($scope.currentEntities)
            }, function errorCallback(response) {
                // called asynchronously if an error occurs
                // or server returns response with an error status.
                // console.log(response)
            });
        }
        // console.log($scope.catbool);

    };
    $scope.getUsers();
    function getNewMatches(availableUsers) {
        var i;
        console.log(availableUsers);
        $scope.suggestedMatches = [];
        for (i = 0; i < 5; i++) {
            var p1 = availableUsers.members[Math.floor(Math.random() * availableUsers.members.length)];
            var p2 = availableUsers.members[Math.floor(Math.random() * availableUsers.members.length)];
            $scope.suggestedMatches.push(
                {
                    "user1": {
                        "img": p1.profile.image_32,
                        "imglg": p1.profile.image_48,
                        "name": p1.name,
                        "id": p1.id
                    },
                    "user2": {
                        "img": p2.profile.image_32,
                        "imglg": p2.profile.image_48,
                        "name": p2.name,
                        "id": p2.id
                    }
                });
        }

    }

    $scope.getGraphData = function (entityid) {
        $scope.graphstatebool = true;
        $scope.userOne.score = 23;
        $scope.userOne.tags = [
            "Zika", "IBM", "Watson",
            "Awesome", "Sauce", "Juice",
            "Chicken", "Rice", "Fufu",
            "Orange Soda", "Tech", "Life"
        ];
        $http({
            url: '/api/getexploredata',
            method: "POST",
            headers: {'Content-Type': 'application/json'},
            data: JSON.stringify(entityid)
        }).success(function (data) {

            if (data == [])
                $scope.graphstatebool = false;

            var nodes = $scope.alchemy.get.allNodes("all");
            var edges = $scope.alchemy.get.allEdges();


            $scope.alchemy.remove.nodes(nodes);
            $scope.alchemy.remove.edges(edges);
            var iEl = angular.element(document.querySelector('#alchemy > svg:nth-child(1)'));
            iEl.remove();
            // $scope.alchemy.updateGraph();


            //
            // $scope.alchemy.a.remove.allNodes("all");
            // $scope.alchemy.a.remove.allEdges();

            var textArray = [
                'links',
                'channels',
                'messages',
                'users',
                'tags'
            ];
            $scope.returneddata = data;
            // data.nodes.forEach(function (node) {
            //     var randomNumber = Math.floor(Math.random() * textArray.length);
            //     node.type = textArray[randomNumber]
            // });
            $scope.some_data = {
                "nodes": data.nodes,
                "edges": data.rels
                //     [{
                //     "id": 290,
                //     "source": 1,
                //     "target": 7,
                //     "value": "By"
                // }]
            }
            ;
            // console.log(data, "Got graph data");
            $scope.config = {
                dataSource: $scope.some_data,
                forceLocked: false,
                directedEdges: true,
                zoomControls: true,
                initialScale: .8,
                initialTranslate: [100, 100],
                nodeTypes: {
                    "type": ["users",
                        "links",
                        "messages", "channels", "Tags"]
                },
                nodeStyle: {
                    "users": {
                        color: "#00ff0e",
                        borderColor: "#D3D3D3"
                    },
                    "links": {
                        color: "#428bca",
                        borderColor: "#D3D3D3"
                    },
                    "messages": {
                        color: "#ff7921",
                        borderColor: "#D3D3D3"
                    },
                    "channels": {
                        color: "#ffffff",
                        borderColor: "#D3D3D3"
                    },
                    "Tags": {
                        color: "#d2322d",
                        borderColor: "#D3D3D3"
                    }
                }
                // graphHeight: function() {return $window.innerHeight/2},
                // graphWidth: function() {return $window.innerWidth/4}
            };

            $scope.alchemy = new $window.Alchemy($scope.config);
            // console.log($scope.alchemy, $window.Alchemy)

        }, function errorCallback(response) {
            // called asynchronously if an error occurs
            // or server returns response with an error status.
            // console.log(response)
        });

    };
    $scope.getUserOneData = function (id) {
        $scope.userOne.score = 23;
        $scope.userOne.tags = [
            "Zika", "IBM", "Watson",
            "Awesome", "Sauce", "Juice",
            "Chicken", "Rice", "Fufu",
            "Orange Soda", "Tech", "Life"
        ];
    };
    $scope.updateMatch = function (match) {
        // console.log(match);
        $scope.userOne = match.user1;
        $scope.userTwo = match.user2;
        $scope.userTwoBool = true;
        $scope.userOneBool = true;
        $scope.selectDisabled = "";
        $scope.samplescore1 = 23;
        $scope.samplescore2 = 95;
        $scope.sampletags = [
            "Zika", "IBM", "Watson",
            "Biotech", "Genetics", "Amurrica",
            "SynBio", "Python", "Testing",
            "DNA", "BioBreaks", "Life"];
    };
    $scope.updateUserTwo = function (user2) {
        $scope.userTwo = user2;
        $scope.userTwoBool = true;
        if (!$scope.userOneBool && !$scope.userTwoBool) {
            $scope.selectDisabled = "";
        }
        // getNewMatches($scope.responseobject)
    };
    $scope.sendMatch = function () {
        $scope.switchConnectInner();
        $scope.introText = "";
    };
    $scope.testAPI();


}


