(function () {
  'use strict';
  angular.module('admin')
    .controller('ManageController', function ($scope, PS_SERVER) {
      $scope.trainList = [];
      $scope.workerList = [];
      $scope.psList = [];
      $scope.psDetail = {};
      $scope.statOfTrain = {};
      $scope.isShowCreateRow = false;

      $scope.newTrain = {
        tId: '',
        codeName: '',
        workerNum: 1,
      };

      $scope.$on('$viewContentLoaded', () => {
        axios.get(PS_SERVER)
          .then(res => {
            const raw = humps.camelizeKeys(res.data);
            console.log(raw);

            const {train, worker, ps, psDetail, statOfTrain} = raw;
            console.log(ps);
            console.log(psDetail);
            $scope.trainList = train;
            $scope.workerList = worker;
            $scope.psDetail = psDetail;
            $scope.statOfTrain = statOfTrain;
            $scope.psList = ps;
            for (let i = 0; i < $scope.psList.length; i++) {
              $scope.psList[i]['isShow'] = false;
            }
            $scope.$apply();

            console.log('@@@@', $scope.trainList, $scope.workerList, $scope.psList);
          })
          .catch(err => console.error(err));
      });

      $scope.toogleShowPSLog = (index) => {
        $scope.psList[index].isShow = !$scope.psList[index].isShow;
      };

      $scope.getPSLog = (index) => {
        let log = '';
        const groupId = $scope.psList[index].groupId;
        $scope.psDetail.forEach((l, idx) => {
          if (l.groupId === groupId) {
            log += (`[${l.workerId}] [${l.time}] ${l.msg}\n`);
          }
        });
        return log;
      };

      $scope.toogleCreateButton = () => {
        if ($scope.isShowCreateRow) {
          $scope.newTrain = {
            tId: '',
            codeName: '',
            workerNum: 1,
          };
        }

        $scope.isShowCreateRow = !$scope.isShowCreateRow;
      };

      $scope.addTrainItem = () => {
        const {tId, codeName, workerNum} = $scope.newTrain;

        $scope.trainList.unshift({
          trainId: tId,
          codeName: codeName,
          workerNum: workerNum,
          status: 'idle'
        });

        $scope.toogleCreateButton();
      };

    });
})();
