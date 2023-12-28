/*

cron: 0 8,18 * * *
const $ = new Env('阿里云盘');

*/



const axios = require('axios')
const {
	initInstance,
	getEnv,
	updateCkEnv
} = require('./qlApi.js')
const notify = require('./sendNotify')

const updateAccesssTokenURL = 'https://auth.aliyundrive.com/v2/account/token'
const signinURL =
	'https://member.aliyundrive.com/v2/activity/sign_in_list?_rx-s=mobile'
const rewardURL =
	'https://member.aliyundrive.com/v1/activity/sign_in_reward?_rx-s=mobile'
const rewardTaskURL =
	'https://member.aliyundrive.com/v2/activity/sign_in_task_reward?_rx-s=mobile'

// 使用 refresh_token 更新 access_token
function updateAccesssToken(queryBody, remarks) {
	const errorMessage = [remarks, '更新 access_token 失败']
	return axios(updateAccesssTokenURL, {
			method: 'POST',
			data: queryBody,
			headers: {
				'Content-Type': 'application/json'
			}
		})
		.then(d => d.data)
		.then(d => {
			const {
				code,
				message,
				nick_name,
				refresh_token,
				access_token
			} = d
			if (code) {
				if (
					code === 'RefreshTokenExpired' ||
					code === 'InvalidParameter.RefreshToken'
				)
					errorMessage.push('refresh_token 已过期或无效')
				else errorMessage.push(message)
				return Promise.reject(errorMessage.join(', '))
			}
			return {
				nick_name,
				refresh_token,
				access_token
			}
		})
		.catch(e => {
			errorMessage.push(e.message)
			return Promise.reject(errorMessage.join(', '))
		})
}

//签到列表
function sign_in(access_token, remarks) {
	const sendMessage = [remarks]
	return axios(signinURL, {
			method: 'POST',
			data: {},
			headers: {
				Authorization: access_token,
				'Content-Type': 'application/json'
			}
		})
		.then(d => d.data)
		.then(async json => {
			if (!json.success) {
				sendMessage.push('签到失败 😹', json.message)
				return Promise.reject(sendMessage.join(', '))
			}
			sendMessage.push('签到成功 🎉')
			const {
				signInInfos,
				signInCount
			} = json.result
			const currentSignInfo = signInInfos[signInCount - 1] // 当天签到信息
			sendMessage.push(`本月累计签到 ${signInCount} 天`)

			rewards = currentSignInfo.rewards
			for await (reward of rewards) {

				if (reward.type === "dailySignIn") {
					const rewardInfo = await getReward(access_token, signInCount)
					sendMessage.push(
						`登录奖励: ${rewardInfo.notice || ''}`)
				} else {
					try {
						const ri = await getRewardTask(access_token, signInCount)
						sendMessage.push(
							`任务奖励: ${ri.notice || ''}`)
					} catch (e) {
						sendMessage.push(`任务奖励: ${e}`)
					}

				}
			}


			return sendMessage.join('\n ')
		})
		.catch(e => {
			sendMessage.push('签到失败 😹')
			sendMessage.push(e.message)
			return Promise.reject(sendMessage.join(', '))
		})
}

// 领取签到奖励
async function getReward(access_token, signInDay) {
	return axios(rewardURL, {
			method: 'POST',
			data: {
				signInDay
			},
			headers: {
				authorization: access_token,
				'Content-Type': 'application/json'
			}
		})
		.then(d => d.data)
		.then(json => {
			if (!json.success) {
				return Promise.reject(json.message)
			}

			return json.result
		})
}

// 领取任务奖励
async function getRewardTask(access_token, signInCount) {
	try {
		const response = await axios.post(rewardTaskURL, {
			signInDay: signInCount
		}, {
			headers: {
				authorization: access_token,
				'Content-Type': 'application/json'
			}
		});
		const json = response.data;
		if (!json.success) {
			if (json.code === 'RepeatExchange') {
				console.log('奖励已领取过');
				return Promise.resolve(json); // 可以选择直接返回或做其他处理
			} else {
				return Promise.reject(json.message);
			}
		}
		return json.result;
	} catch (error) {
		return Promise.reject("奖励已领取过");
	}
}


// 获取环境变量
async function getRefreshToken() {
		let instance = null
		try {
			instance = await initInstance()
		} catch (e) {}

		let refreshToken = process.env.refreshToken || []
		try {
			if (instance) refreshToken = await getEnv(instance, 'refreshToken')
		} catch (e) {}

		let refreshTokenArray = []

		if (Array.isArray(refreshToken)) refreshTokenArray = refreshToken
		else if (refreshToken.indexOf('&') > -1)
			refreshTokenArray = refreshToken.split('&')
		else if (refreshToken.indexOf('\n') > -1)
			refreshTokenArray = refreshToken.split('\n')
		else refreshTokenArray = [refreshToken]

		if (!refreshTokenArray.length) {
			console.log('未获取到refreshToken, 程序终止')
			process.exit(1)
		}

		return {
			instance,
			refreshTokenArray
		}
	}

	!(async () => {
		const {
			instance,
			refreshTokenArray
		} = await getRefreshToken()

		const message = []
		let index = 1
		for await (refreshToken of refreshTokenArray) {
			let remarks = refreshToken.remarks || `账号${index}`
			const queryBody = {
				grant_type: 'refresh_token',
				refresh_token: refreshToken.value || refreshToken
			}

			try {
				const {
					nick_name,
					refresh_token,
					access_token
				} =
				await updateAccesssToken(queryBody, remarks)

				if (nick_name && nick_name !== remarks)
					remarks = `${nick_name}(${remarks})`

				// 更新环境变量
				if (instance) {
					let params = {
						name: refreshToken.name,
						value: refresh_token,
						remarks: refreshToken.remarks || nick_name // 优先存储原有备注信息
					}
					// 新版青龙api
					if (refreshToken.id) {
						params.id = refreshToken.id
					}
					// 旧版青龙api
					if (refreshToken._id) {
						params._id = refreshToken._id
					}
					await updateCkEnv(instance, params)
				}

				const sendMessage = await sign_in(access_token, remarks)
				console.log(sendMessage)
				console.log('\n')
				message.push(sendMessage)
			} catch (e) {
				console.log(e)
				console.log('\n')
				message.push(e)
			}
			index++
		}
		await notify.sendNotify(`阿里云盘签到`, message.join('\n'))
	})()
